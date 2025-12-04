FROM python:3.11-slim

# Set the working directory
WORKDIR /home

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential python3-dev gcc libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Copy requirements and install dependencies
COPY ./containers/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./art-kb-schema ./art-kb-schema

RUN pip install --no-cache-dir --upgrade ./art-kb-schema

# Copy application code
COPY ./api ./api

# Copy and make the entrypoint script executable
COPY ./containers/backend/docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

COPY ./containers/backend/logging.conf .

# Set the entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]