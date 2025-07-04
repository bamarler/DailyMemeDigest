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
ENV MEME_MODE=cloud

# Run meme.py directly with Cloud Run's PORT
# Note: meme.py expects "python meme.py cloud 8080" format
CMD exec python meme.py cloud $PORT