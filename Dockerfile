FROM python:3.12-slim

# Install Poetry
RUN pip install poetry

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Copy the application code
COPY ./mempool /app

# Define build arguments
ARG KAFKA_BROKER
ARG KAFKA_TOPIC
ARG WSS_URL
ARG KAFKA_GROUP

# Set environment variables
ENV KAFKA_BROKER=${KAFKA_BROKER}
ENV KAFKA_TOPIC=${KAFKA_TOPIC}
ENV MEMPOOL_API=${WSS_URL}
ENV KAFKA_GROUP=${KAFKA_GROUP}

COPY .env /app

