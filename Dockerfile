# Use official slim Python 3.10 base image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl and download wait-for-it.sh script for service readiness check
RUN apt-get update && apt-get install -y curl && \
    curl -o wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x wait-for-it.sh

# Copy application code into the container
COPY . .

# Wait for DB service to be ready, then run fetch_data.py
CMD ["sh", "-c", "./wait-for-it.sh \"$DB_HOST:$DB_PORT\" -- python fetch_data.py"]
