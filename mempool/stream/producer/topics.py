from mempool.config.logging import setup_logger
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import (
    StringSerializer,
    SerializationContext,
    MessageField,
)
from mempool.stream.producer.model import Transaction
from mempool.config.provider import get_schema_registry, get_admin_client, get_producer
from confluent_kafka.admin import NewTopic
from typing import Dict
import json

logger = setup_logger(name="topics")


async def create_topic(
    topic_name: str, num_partitions: int = 1, replication_factor: int = 1
):
    admin_client = await get_admin_client()
    topic_metadata = admin_client.list_topics(timeout=10)
    if topic_name in topic_metadata.topics:
        logger.info(f"Topic '{topic_name}' already exists, attaching to it.")
    else:
        new_topic = NewTopic(topic_name, num_partitions, replication_factor)
        topic = admin_client.create_topics(new_topics=[new_topic])

        for topic, f in topic.items():
            try:
                f.result()
                logger.info(f"Topic '{topic_name}' created successfully.")
                return topic_name
            except Exception as e:
                logger.error(f"Failed to create topic '{topic_name}': {str(e)}")


async def get_schema() -> str:
    with open("/app/mempool/stream/producer/schema.json") as f:
        schema = json.load(f)  # type: Dict
    return json.dumps(schema)


async def get_serializer():
    json = await get_schema()
    schema_registry = await get_schema_registry()
    return JSONSerializer(
        schema_str=json, schema_registry_client=schema_registry
    )  # Convert schema to string


async def send_transaction_to_kafka(
    transaction_data: Transaction, topic_name: str, producer
):
    key = transaction_data.hash
    serialiser = await get_serializer()
    string_serialiser = StringSerializer("utf_8")
    producer.produce(
        topic=topic_name,
        key=string_serialiser(key),
        value=serialiser(
            transaction_data.dict(),
            SerializationContext(topic=topic_name, field=MessageField.VALUE),
        ),
        on_delivery=delivery_report,
    )
    producer.flush()


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
