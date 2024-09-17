FROM python:3.12-slim



RUN pip install poetry

# Set work directory
WORKDIR /app/mempool

# Copy project files
COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-interaction --no-ansi

# Copy the application code
COPY ./mempool /app

# Install debugpy
RUN pip install debugpy

# Set environment variables
ENV PYTHONPATH=/app

COPY .env /app

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

# Set work directory
WORKDIR /app/mempool

# The command will be overridden by docker-compose
CMD ["poetry", "run", "python", "-m", "mempool.main_producer"]