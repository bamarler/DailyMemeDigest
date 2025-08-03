FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn for production
RUN pip install gunicorn

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV ENVIRONMENT=production

# Expose port (documentation only)
EXPOSE 8080

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/v1/health || exit 1

# Run the Flask app with gunicorn
# Cloud Run will set PORT environment variable
# Note: create_app() returns the app instance
# --timeout 300: Allow 5 minutes for long-running meme generation
# --workers 1: Use single worker for SSE support
# --threads 8: Handle multiple concurrent requests
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 300 "app:app"