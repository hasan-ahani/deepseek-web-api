FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT=120000 \
    HOST=0.0.0.0 \
    PORT=8000 \
    SERVER_INTERACTIVE_LOGIN=0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer caching), then the Chromium build the
# bundled Playwright expects so client versions always match. --with-deps pulls
# the OS shared libraries Chromium needs.
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 --retries 10 -r requirements.txt \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Run unprivileged; the mounted session volume must be writable by uid 1000.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/session \
    && chown -R appuser:appuser /app /ms-playwright
USER appuser

EXPOSE 8000

CMD ["uvicorn", "server.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
