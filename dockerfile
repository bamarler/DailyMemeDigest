FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create necessary directories
RUN mkdir -p database static/css static/js templates src

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV MEME_MODE=cloud

# Use gunicorn with the WSGI entry point
# Cloud Run provides PORT environment variable
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 wsgi:app