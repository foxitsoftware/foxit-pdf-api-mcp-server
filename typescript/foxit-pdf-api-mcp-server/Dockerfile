# Build stage
# FROM jfrog.foxitsoftware.com/docker-release/cops/node:23.4-alpine3.20 AS builder
FROM node:22-alpine3.20 AS builder

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
# FROM jfrog.foxitsoftware.com/docker-release/cops/node:23.4-alpine3.20
FROM node:22-alpine3.20 AS production

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

# Expose the port
EXPOSE 8080

# Start the HTTP server
CMD ["node", "dist/http-server.js"]
