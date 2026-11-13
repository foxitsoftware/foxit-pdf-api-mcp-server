/**
 * Filesystem path guards for the document lifecycle tools.
 *
 * The MCP server may be exposed over HTTP/network. Without these checks,
 * `upload_document` (resourceUri) and `download_document` (outputPath) let a
 * remote caller read or write arbitrary local files — SSH keys, cloud
 * credentials, `~/.ssh/authorized_keys`, shell startup files, etc.
 *
 * Strategy (symmetric allow-list, mirroring foxit-esign-mcp):
 *  - Reject `..` traversal segments outright.
 *  - Resolve symlinks via realpath before checking, so a link inside an
 *    allowed directory that points to a sensitive path outside is rejected.
 *  - Only permit paths that live inside one of the allowed directories.
 *
 * Allowed roots default to the user's Downloads/Desktop/Documents plus the
 * OS temp dir. Override with a colon-separated `MCP_FS_ALLOWED_DIRS` env var.
 */
import { realpathSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join, resolve, sep } from "node:path";

/** Resolve a directory through realpath when it exists (e.g. /tmp -> /private/tmp). */
function realDir(dir: string): string {
  const abs = resolve(dir);
  try {
    return realpathSync(abs);
  } catch {
    return abs;
  }
}

/** Directories reads/writes are confined to. */
export const ALLOWED_DIRS: string[] = (() => {
  const override = process.env.MCP_FS_ALLOWED_DIRS?.trim();
  const base = override
    ? override
        .split(":")
        .map((d) => d.trim())
        .filter(Boolean)
    : [
        join(homedir(), "Downloads"),
        join(homedir(), "Desktop"),
        join(homedir(), "Documents"),
        tmpdir(),
        "/tmp",
      ];
  // Include both the lexical path and its realpath (handles /tmp -> /private/tmp).
  const set = new Set<string>();
  for (const dir of base) {
    set.add(resolve(dir));
    set.add(realDir(dir));
  }
  return [...set];
})();

function isWithinAllowed(resolvedPath: string): boolean {
  return ALLOWED_DIRS.some(
    (dir) => resolvedPath === dir || resolvedPath.startsWith(dir + sep)
  );
}

/**
 * Validate a path we are about to READ (local file upload).
 * Returns an error string if disallowed, or `null` if safe.
 */
export function validateReadPath(filePath: string): string | null {
  if (!filePath || filePath.includes("\0")) {
    return "filePath is empty or contains a null byte.";
  }
  if (filePath.includes("..")) {
    return "filePath must not contain '..' path traversal segments.";
  }

  // Resolve symlinks first — critical to block `~/Downloads/evil -> /etc/passwd`.
  let real: string;
  try {
    real = realpathSync(filePath);
  } catch {
    // File doesn't exist yet — fall back to lexical resolution. The final
    // allow-list check below still confines it.
    real = resolve(filePath);
  }

  if (!isWithinAllowed(real)) {
    return (
      `filePath must be within one of: ${ALLOWED_DIRS.join(", ")}. ` +
      `Resolved path: ${real}`
    );
  }
  return null;
}

/**
 * Validate a path we are about to WRITE (document download).
 * Returns an error string if disallowed, or `null` if safe.
 */
export function validateSavePath(savePath: string): string | null {
  if (!savePath || savePath.includes("\0")) {
    return "outputPath is empty or contains a null byte.";
  }
  if (savePath.includes("..")) {
    return "outputPath must not contain '..' path traversal segments.";
  }

  // The target may not exist yet, so resolve dirname's symlinks where possible
  // then re-join the basename, preventing symlinked-dir escapes.
  const resolved = resolve(savePath);
  let real = resolved;
  try {
    real = join(realpathSync(resolve(resolved, "..")), resolved.split(sep).pop() ?? "");
  } catch {
    // parent doesn't exist — keep lexical resolution
  }

  if (!isWithinAllowed(real)) {
    return (
      `outputPath must be within one of: ${ALLOWED_DIRS.join(", ")}. ` +
      `Resolved path: ${real}`
    );
  }
  return null;
}

/**
 * Convert a `file://` URI to a filesystem path, handling localhost authority
 * and percent-encoding. Returns null if the URI is not a usable file URI.
 */
export function fileUriToPath(resourceUri: string): string | null {
  try {
    const url = new URL(resourceUri);
    if (url.protocol !== "file:") return null;
    // Reject non-local authorities (e.g. file://evil-host/path).
    if (url.host && url.host !== "localhost") return null;
    return decodeURIComponent(url.pathname);
  } catch {
    return null;
  }
}
