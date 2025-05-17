FROM --platform=linux/amd64 python:3.10-slim-buster

# Install system dependencies required for BigQuery
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/myapp

# Install Python dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PORT=8080

# Expose the correct port (must match Cloud Run --port)
EXPOSE 8080

# Run Gunicorn with basic configuration
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:app"]