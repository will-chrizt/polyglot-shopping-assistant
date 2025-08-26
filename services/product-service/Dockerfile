# Stage 1: Build dependencies
FROM node:18-alpine AS builder

WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# Copy source code
COPY . .

# Optional: Build step (e.g., for TypeScript or bundlers)
# RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy only what's needed from builder
COPY --from=builder /app ./

# Switch to non-root user
USER appuser

# Health check endpoint (optional)
HEALTHCHECK --interval=30s --timeout=10s \
  CMD wget --spider http://localhost:3000/health || exit 1

EXPOSE 8001

CMD ["node", "index.js"]
