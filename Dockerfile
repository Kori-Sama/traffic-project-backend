FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required by psycopg2 and shapely
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (layer caching: only re-install when requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
        tensorflow>=2.19.0 \
        pandas>=2.2.3 \
        scikit-learn>=1.6.1 \
        psycopg2-binary>=2.9.11 \
        tqdm>=4.67.3

# Copy application code
COPY . .

# Ensure videos directory exists (mounted as static files at /videos)
RUN mkdir -p /app/videos

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
