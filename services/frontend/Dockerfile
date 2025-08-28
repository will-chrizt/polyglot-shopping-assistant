# syntax=docker/dockerfile:1

# --- Stage 1: Build Environment ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=8000

WORKDIR /app

# Install system and Python dependencies in one layer
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# --- Stage 2: Runtime Environment ---
FROM python:3.11-slim AS runtime

ENV PORT=8000

WORKDIR /app

# Copy only what's needed from builder stage
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /app /app

EXPOSE 8000

ENTRYPOINT ["python", "frontend-service.py"]
