#! /usr/bin/env node

import {server} from "./server"

// Start server
server.start({
  transportType: "stdio",
});
