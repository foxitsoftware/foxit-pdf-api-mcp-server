# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-11-13

### Security

- **HTTP transport binds to loopback by default.** The default `--host` is now
  `127.0.0.1` (previously `0.0.0.0`). The server refuses to start when bound to
  a non-loopback interface without authentication.
- **Bearer-token authentication for the HTTP transport.** Set `MCP_AUTH_TOKEN`
  (or `--auth-token`). HTTP requests must send `Authorization: Bearer <token>`;
  unauthenticated requests are rejected before any tool executes. Token
  comparison is constant-time. The stdio transport is unaffected.
- **Restricted local file reads in `upload_document`.** `resourceUri` file reads
  are now confined to an allow-list of directories (`~/Downloads`, `~/Desktop`,
  `~/Documents`, and the OS temp directory; override with `MCP_FS_ALLOWED_DIRS`).
  Paths are `realpath`-resolved to prevent symlink escapes; `..` traversal and
  non-local `file://` authorities are rejected.
- **Restricted local file writes in `download_document`.** `outputPath` writes
  are confined to the same allow-list, with the same traversal and symlink
  protections.

### Changed

- Docker image sets `SERVER_HOST=0.0.0.0` for container networking; a token
  (`MCP_AUTH_TOKEN`) is required and enforced for that non-loopback binding.
- `.env.example` and README document `MCP_AUTH_TOKEN`, `MCP_FS_ALLOWED_DIRS`,
  and the new default host, including guidance that a token is required for any
  non-loopback deployment.

### Fixed

- Download/upload tools no longer allow reading or writing arbitrary files
  outside the configured directories.

[1.2.0]: https://github.com/foxitsoftware/foxit-pdf-api-mcp-server/compare/v1.1.2...v1.2.0
