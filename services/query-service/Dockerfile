FROM node:20-slim AS builder
WORKDIR /app

# Copy package files and install dependencies
# This layer is cached to speed up future builds
COPY package*.json ./
RUN npm ci --omit=dev

# Copy the rest of the application code
COPY . .

# Stage 2: Final runtime image
FROM node:20-slim
WORKDIR /app

# Copy only the necessary files from the builder stage
# Set ownership to the built-in 'node' user for better security
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/query-service.js ./

# Switch to the non-root 'node' user
USER node

# Expose the port the app runs on
EXPOSE 8002


# The command to run the application
ENTRYPOINT ["node", "query-service.js"]
