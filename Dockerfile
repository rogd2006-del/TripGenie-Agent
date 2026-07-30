FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirement specifications
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY server /app/server

EXPOSE 8000

ENV PYTHONPATH=/app/server

CMD ["python", "server/main.py"]
