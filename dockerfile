FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    gcc \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY assets/ ./assets/

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python3 -c 'import urllib.request; urllib.request.urlopen("http://localhost:8080/").getcode()' || exit 1

# Run the bot
CMD ["python3", "-m", "src"]
