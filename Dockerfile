# ── Security-hardened Dockerfile ────────────────────────────────
# Base image: pinned to specific version — never use :latest
# Slim variant: fewer packages = smaller attack surface
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependencies first — better layer caching
# Docker only rebuilds this layer when requirements.txt changes
COPY src/requirements.txt .

# Install dependencies
# --no-cache-dir: reduces image size, no cached packages to exploit
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ .

# Create non-root user — CIS Benchmark requirement
# Running as root = if container is compromised, attacker has root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Document which port the app uses
EXPOSE 8080

# Health check — Kubernetes uses this for readiness/liveness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run the application
ENTRYPOINT ["python", "app.py"]
