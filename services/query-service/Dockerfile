# Stage 1: Build dependencies
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
# Use npm ci for reproducible builds
RUN npm ci --omit=dev
COPY . .

# Stage 2: Final runtime image
FROM node:20-slim
WORKDIR /app

# Copy built artifacts and application code from the builder stage
# and set ownership to the built-in 'node' user in one step.
COPY --from=builder --chown=node:node /app ./

# Switch to the non-root 'node' user
USER node

# Expose the port the app runs on
EXPOSE 8002

# The command to run the application
ENTRYPOINT ["node", "query-service.js"]
