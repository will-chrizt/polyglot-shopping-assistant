# Stage 1: Build dependencies
# Use Node 20 LTS slim for better performance, security, and compatibility.
FROM node:20-slim AS builder
WORKDIR /app

# Copy package files and install production dependencies.
# This layer is cached to speed up future builds.
COPY package*.json ./
RUN npm ci --omit=dev

# Copy the rest of the application source code.
# A .dockerignore file is recommended to exclude unnecessary files.
COPY . .

# Stage 2: Final runtime image
FROM node:20-slim
WORKDIR /app

# Copy artifacts from the builder stage, setting ownership to the built-in 'node' user.
# This is more efficient than copying the entire /app directory.
COPY --from=builder --chown=node:node /app/package*.json ./
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/src ./src

# Switch to the secure, built-in non-root 'node' user.
USER node

# Expose the port the application runs on.
EXPOSE 8001

# Use CMD to run the application. It provides a default that's easily overridden.
ENTRYPOINT ["node", "src/index.js"]
