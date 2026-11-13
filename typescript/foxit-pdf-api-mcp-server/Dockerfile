# Build stage
FROM node:24-alpine AS builder

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.21.0 --activate

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source files
COPY . .

# Build the application
RUN pnpm run build

# Production stage
FROM node:24-alpine AS production

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.21.0 --activate

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install only production dependencies
RUN pnpm install --frozen-lockfile --prod

# Copy built files from builder
COPY --from=builder /app/dist ./dist

# Set environment variables
ENV NODE_ENV=production
ENV SERVER_PORT=8080
# Bind all interfaces inside the container; a bearer token (MCP_AUTH_TOKEN) is
# REQUIRED when exposing a non-loopback host, so the container refuses to start
# without it. Supply it at runtime, e.g.: docker run -e MCP_AUTH_TOKEN=...
ENV SERVER_HOST=0.0.0.0

# Expose the port
EXPOSE 8080

# Start the HTTP stream server
CMD ["node", "dist/main.js", "--transport", "httpStream"]
