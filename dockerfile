# Multi-stage build for efficiency
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy package files first for better caching
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci --only=production

# Copy all frontend source code
COPY frontend/ ./

# Set environment variables for build
ENV REACT_APP_API_BASE_URL=
ENV NODE_ENV=production

# Build the React app
RUN npm run build

# Stage 2: Python runtime with built frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
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

# Copy application code (excluding frontend/node_modules and build)
COPY app.py .
COPY .env .

# Copy built frontend from the frontend-builder stage
COPY --from=frontend-builder /frontend/build ./frontend/build

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV ENVIRONMENT=production
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Run the Flask app with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 300 "app:app"