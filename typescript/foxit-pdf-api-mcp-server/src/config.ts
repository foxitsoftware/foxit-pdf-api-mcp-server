// Configuration from environment variables
const DEFAULT_API_BASE_URL = "https://na1.fusion.foxit.com/pdf-services";
let API_BASE_URL =
  process.env.FOXIT_CLOUD_API_BASE_URL ||
  process.env.FOXIT_CLOUD_API_HOST ||
  DEFAULT_API_BASE_URL;
const CLIENT_ID = process.env.FOXIT_CLOUD_API_CLIENT_ID ?? "";
const CLIENT_SECRET = process.env.FOXIT_CLOUD_API_CLIENT_SECRET ?? "";

if (!API_BASE_URL) {
  console.error(
    "Error: FOXIT_API_BASE_URL or FOXIT_CLOUD_API_HOST environment variable is required"
  );
  process.exit(1);
}

// validate API_BASE_URL formatting and fix if needed
try {
  new URL(API_BASE_URL); // Validate URL format
} catch (error) {
  console.error(`Error: Invalid API base URL format: ${API_BASE_URL}`);
  process.exit(1);
}
API_BASE_URL = API_BASE_URL.replace(/\/+$/, ""); // Remove trailing slashes

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error(
    "Error: FOXIT_CLOUD_API_CLIENT_ID and FOXIT_CLOUD_API_CLIENT_SECRET environment variables are required"
  );
  process.exit(1);
}

export const config = {
  apiBaseUrl: API_BASE_URL,
  clientId: CLIENT_ID,
  clientSecret: CLIENT_SECRET,
  defaultTimeout: 300000, // 5 minutes
  pollInterval: 2000, // 2 seconds
  maxRetries: 3,
};

export type Config = typeof config;
