# syntax=docker/dockerfile:1

# Stage 1: Build dependencies
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && mkdir -p /app/src
COPY . .

# Stage 2: Runtime
FROM node:18-alpine
WORKDIR /app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup && chown -R appuser:appgroup /app
COPY --from=builder /app ./
USER appuser
EXPOSE 8002
ENTRYPOINT ["node", "query-service.js"]
