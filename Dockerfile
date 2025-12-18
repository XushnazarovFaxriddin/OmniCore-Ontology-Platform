# OmniCore Platform v10 - Production Dockerfile
# AI-Orchestrated Ontological Computing System
# Target: PARAM BILIM Supercomputer (AlmaLinux 8.9)

FROM python:3.11-slim as builder

# Build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Production image
FROM python:3.11-slim

# Labels
LABEL maintainer="Kaizen Group <kaizen@buxsu.uz>"
LABEL version="10.0.0"
LABEL description="OmniCore Ontology Platform v10"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 10000 -s /bin/bash omnicore

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create app directories
RUN mkdir -p /app/data /app/logs /app/snapshots /app/ontologies && \
    chown -R omnicore:omnicore /app

# Copy application code
WORKDIR /app
COPY --chown=omnicore:omnicore . .

# Switch to non-root user
USER omnicore

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${OMNICORE_PORT:-8000}/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "src.core.gateway.api:app", "--host", "0.0.0.0", "--port", "8000"]
