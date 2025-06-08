FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download wait-for-it.sh during build
RUN apt-get update && apt-get install -y curl && \
    curl -o wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x wait-for-it.sh

COPY . .

CMD ["sh", "-c", "./wait-for-it.sh \"$DB_HOST:$DB_PORT\" -- python fetch_data.py"]
