# tests/test_producer.py
import pytest
import os


@pytest.mark.asyncio
async def test_producer(async_kafka_producer, async_mempool_data):
    kafka_topic = os.getenv("KAFKA_TOPIC")
    assert (
        kafka_topic == "mempool"
    ), "Environment variable KAFKA_TOPIC not set correctly"

    # Simulate sending transactions to Kafka
    for tx in async_mempool_data["transactions"]:
        result = await async_kafka_producer.send(kafka_topic, tx["txid"])
        assert "Produced to topic" in result
        print(result)  # For debugging purposes
