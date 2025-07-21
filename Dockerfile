# Use official Python image
FROM python:3.12-slim

# Install system dependencies for psycopg2 and pgvector
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Chainlit default port
EXPOSE 8000

# Set environment variables (optional, can be overridden in docker-compose)
ENV PYTHONUNBUFFERED=1

# Start Chainlit app
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]