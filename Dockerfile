FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libzbar0 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Buat direktori untuk file temporary
RUN mkdir -p /tmp/tikqr_bot

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Jakarta

# Run the bot
CMD ["python", "bot.py"]
