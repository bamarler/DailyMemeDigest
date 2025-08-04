# Multi-stage build for efficiency
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files explicitly
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies with ci for faster, reproducible builds
RUN npm ci

# Copy frontend source code
COPY frontend/ ./

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

# Copy application code
COPY . .

# Copy built frontend from the frontend-builder stage
COPY --from=frontend-builder /frontend/build ./frontend/build

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV ENVIRONMENT=production

# Expose port (documentation only)
EXPOSE 8080

# Run the Flask app with gunicorn
# Cloud Run will set PORT environment variable
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 300 "app:app"