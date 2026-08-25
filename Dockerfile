# Official Playwright Python image with Chromium & OS dependencies pre-installed
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PROMAS_CACHE_DIR=/app/.cache

WORKDIR /app

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY promas/ ./promas/

# Install Promas package and dependencies
RUN pip install --no-cache-dir .

# Create cache directory
RUN mkdir -p /app/.cache

# Default to running the FastMCP server over standard I/O
ENTRYPOINT ["promas-mcp"]
