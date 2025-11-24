# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies (including GDAL for Fiona)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# (Optional, but can help Fiona find it explicitly)
ENV GDAL_CONFIG=/usr/bin/gdal-config

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application
COPY backend/ ./backend/

# Expose the port the app runs on
EXPOSE 8007

# Command to run the application
CMD ["python", "backend/main.py"]