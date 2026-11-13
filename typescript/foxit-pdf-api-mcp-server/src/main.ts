#! /usr/bin/env node

import { parseArgs } from "node:util";

/**
 * CLI entry point for the Foxit PDF API MCP Server.
 *
 * Supports the following command-line arguments:
 *
 *   --transport <stdio|httpStream>   Transport type (default: stdio)
 *   --host <host>                    HTTP stream host (default: 0.0.0.0)
 *   --port <port>                    HTTP stream port (default: 8080)
 *   --endpoint <path>                HTTP stream endpoint (default: /mcp)
 *   --stateless                      Enable stateless HTTP stream mode
 *   --enable-json-response           Enable JSON response mode for HTTP stream
 *   --ssl-cert <path>                Path to SSL certificate
 *   --ssl-key <path>                 Path to SSL private key
 *   --ssl-ca <path>                  Path to SSL CA bundle
 *   -h, --help                       Show help
 *
 * Environment variables (for HTTP stream defaults):
 *   SERVER_HOST   Default host (default: 0.0.0.0)
 *   SERVER_PORT   Default port (default: 8080)
 *
 * Examples:
 *   npx @foxitsoftware/foxit-pdf-api-mcp-server --transport stdio
 *   npx @foxitsoftware/foxit-pdf-api-mcp-server --transport httpStream --port 9000
 *   npx @foxitsoftware/foxit-pdf-api-mcp-server --transport httpStream --host 127.0.0.1 --port 8080
 */

const HELP_TEXT = `Foxit PDF API MCP Server

Usage:
  npx @foxitsoftware/foxit-pdf-api-mcp-server [options]

Options:
  --transport <stdio|httpStream>   Transport type (default: stdio)
  --host <host>                    HTTP stream host (default: 0.0.0.0)
  --port <port>                    HTTP stream port (default: 8080)
  --endpoint <path>                HTTP stream endpoint (default: /mcp)
  --stateless                      Enable stateless HTTP stream mode
  --enable-json-response           Enable JSON response mode for HTTP stream
  --ssl-cert <path>                Path to SSL certificate
  --ssl-key <path>                 Path to SSL private key
  --ssl-ca <path>                  Path to SSL CA bundle
  -h, --help                       Show this help message

Environment Variables:
  FOXIT_CLOUD_API_HOST             Foxit API base URL
  FOXIT_CLOUD_API_CLIENT_ID        Foxit API client ID
  FOXIT_CLOUD_API_CLIENT_SECRET    Foxit API client secret
  SERVER_HOST                      Default HTTP stream host (default: 0.0.0.0)
  SERVER_PORT                      Default HTTP stream port (default: 8080)

Examples:
  # Run with stdio transport (default)
  npx @foxitsoftware/foxit-pdf-api-mcp-server --transport stdio

  # Run with HTTP stream transport on port 9000
  npx @foxitsoftware/foxit-pdf-api-mcp-server --transport httpStream --port 9000

  # Run with HTTP stream on a specific host and port
  npx @foxitsoftware/foxit-pdf-api-mcp-server --transport httpStream --host 127.0.0.1 --port 8080
`;

function parseCliArgs() {
  const { values } = parseArgs({
    options: {
      transport: { type: "string" },
      host: { type: "string" },
      port: { type: "string" },
      endpoint: { type: "string" },
      stateless: { type: "boolean", default: false },
      "enable-json-response": { type: "boolean", default: false },
      "ssl-cert": { type: "string" },
      "ssl-key": { type: "string" },
      "ssl-ca": { type: "string" },
      help: { type: "boolean", short: "h", default: false },
    },
    allowNegative: true,
    strict: true,
  });

  return values;
}

async function main() {
  const args = parseCliArgs();

  if (args.help) {
    console.log(HELP_TEXT);
    process.exit(0);
  }

  const transportType = args.transport ?? "stdio";

  if (transportType !== "stdio" && transportType !== "httpStream") {
    console.error(
      `Error: Invalid transport type "${transportType}". Must be "stdio" or "httpStream".`
    );
    console.error(HELP_TEXT);
    process.exit(1);
  }

  if (transportType === "stdio") {
    // Load the server lazily so `--help` works without runtime config/env.
    const { server } = await import("./server");
    await server.start({
      transportType: "stdio",
    });
    return;
  }

  // HTTP stream transport
  const host = args.host ?? process.env.SERVER_HOST ?? "0.0.0.0";
  const port = parseInt(args.port ?? process.env.SERVER_PORT ?? "8080", 10);

  if (Number.isNaN(port) || port < 0 || port > 65535) {
    console.error(`Error: Invalid port "${args.port}". Must be a number between 0 and 65535.`);
    process.exit(1);
  }

  const { server } = await import("./server");
  await server.start({
    transportType: "httpStream",
    httpStream: {
      host,
      port,
      ...(args.endpoint && { endpoint: args.endpoint as `/${string}` }),
      ...(args.stateless && { stateless: true }),
      ...(args["enable-json-response"] && { enableJsonResponse: true }),
      ...(args["ssl-cert"] && { sslCert: args["ssl-cert"] }),
      ...(args["ssl-key"] && { sslKey: args["ssl-key"] }),
      ...(args["ssl-ca"] && { sslCa: args["ssl-ca"] }),
    },
  });
}

main().catch((error) => {
  console.error("Failed to start server:", error);
  process.exit(1);
});
