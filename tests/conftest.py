# tests/conftest.py
import pytest
import os
from dotenv import dotenv_values
import asyncio


@pytest.fixture(autouse=True)
def set_env_variables(monkeypatch):
    """
    This fixture will automatically set environment variables for all tests.
    You can override these variables inside individual tests if needed.
    """
    monkeypatch.setenv("KAFKA_BROKER", dotenv_values(".env")["KAFKA_BROKER"])
    monkeypatch.setenv("KAFKA_TOPIC", dotenv_values(".env")["KAFKA_TOPIC"])
    monkeypatch.setenv("WSS_URL", dotenv_values(".env")["WSS_URL"])
    monkeypatch.setenv("TIMEOUT", os.getenv("TIMEOUT", "30"))


@pytest.fixture
async def async_mempool_data():
    """
    Async fixture to simulate fetching mempool data asynchronously.
    This can be reused across multiple tests.
    """
    await asyncio.sleep(1)  # Simulate delay
    return {"transactions": [{"txid": "12345"}, {"txid": "67890"}]}


@pytest.fixture
async def async_kafka_producer():
    """
    Async fixture to simulate a Kafka producer.
    It would mock the behavior of the actual producer.
    """

    class MockProducer:
        async def send(self, topic, value):
            await asyncio.sleep(0.1)  # Simulate network latency
            return f"Produced to topic {topic} with value {value}"

    return MockProducer()
