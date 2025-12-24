import { server } from "./server";

// Start server
server.start({
  transportType: "httpStream",
  httpStream: {
    host: "0.0.0.0",
    port: parseInt(process.env.SERVER_PORT || "8080", 10),
  },
});
