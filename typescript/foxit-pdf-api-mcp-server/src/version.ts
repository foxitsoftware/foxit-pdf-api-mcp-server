// Injected at build time by tsup `define` (see tsup.config.ts).
declare const __VERSION__: string;

/**
 * Package version, injected at build time.
 * Typed as a semver template literal to satisfy FastMCP's `version` option.
 */
export const VERSION = __VERSION__ as `${number}.${number}.${number}`;
