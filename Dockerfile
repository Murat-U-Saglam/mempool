FROM python:3.12-slim


RUN pip install poetry



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
ENV SCHEMA_REGISTRY_URL=${SCHEMA_REGISTRY_URL}

# Install debugpy
RUN pip install debugpy

ENV PYTHONPATH=/app

COPY . /app

WORKDIR /app

RUN poetry install --no-interaction --no-ansi


CMD ["poetry", "run", "python", "-m", "mempool.main_producer"]