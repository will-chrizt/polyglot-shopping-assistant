# Stage 1: Build dependencies
FROM node:18-alpine AS builder

WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# Copy source code
COPY . .



# Stage 2: Runtime
FROM node:18-alpine

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy only what's needed from builder
COPY --from=builder /app ./

# Switch to non-root user
USER appuser



EXPOSE 8001

ENTRYPOINT ["node", "src/index.js"]
