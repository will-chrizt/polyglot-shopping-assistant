# --- Stage 1: Build Environment ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=8000

WORKDIR /app

# Install system dependencies needed for building Python packages
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# --- Stage 2: Runtime Environment ---
FROM python:3.11.9-slim-bookworm AS runtime

ENV PORT=8000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

WORKDIR /app

# Create a non-root user for better security (Recommended)
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code from the builder stage
COPY --from=builder --chown=nonroot:nonroot /app /app

# Switch to the non-root user
USER nonroot

EXPOSE 8000

# Run the application
ENTRYPOINT ["python", "frontend-service.py"]
