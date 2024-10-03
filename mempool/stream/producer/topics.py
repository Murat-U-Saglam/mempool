from mempool.config.logging import setup_logger
from confluent_kafka.schema_registry.json_schema import JSONSerializer # type: ignore
from confluent_kafka.serialization import (  # type: ignore
    StringSerializer,
    SerializationContext,
    MessageField,
)
from mempool.stream.producer.model import Transaction
from mempool.config.provider import get_schema_registry, get_admin_client
from confluent_kafka.admin import NewTopic # type: ignore
import json
from confluent_kafka.schema_registry import SchemaRegistryError # type: ignore

logger = setup_logger(name="topics")


async def create_topic(
    topic_name: str, num_partitions: int = 1, replication_factor: int = 1
) -> str:
    admin_client = await get_admin_client()
    topic_metadata = admin_client.list_topics(timeout=10)
    if topic_name in topic_metadata.topics:
        logger.info(f"Topic '{topic_name}' already exists, attaching to it.")
        return topic_name
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
                return topic_name
    return topic_name


async def get_schema() -> str:
    with open("/app/mempool/stream/producer/schema.json") as f:
        schema = json.load(f) 
    return json.dumps(schema)


async def get_serializer():
    json = await get_schema()
    schema_registry = await get_schema_registry()
    try:
        schema_registry.delete_subject("transactions-value")
    except SchemaRegistryError:
        pass
    return JSONSerializer(
        schema_str=json, schema_registry_client=schema_registry, 
    ) 


async def send_transaction_to_kafka(
    transaction_data: Transaction, topic_name: str, producer, serialiser
):
    key = transaction_data.hash
    ctx = SerializationContext(topic=topic_name, field=MessageField.VALUE)
    string_serialiser = StringSerializer("utf_8")
    logger.debug(
        f"Attempting to serialise data: {serialiser(transaction_data.model_dump(), ctx)}"
    )
    producer.produce(
        topic=topic_name,
        key=string_serialiser(key),
        value=serialiser(
            transaction_data.dict(),
            ctx,
        ),
        on_delivery=delivery_report,
    )
    producer.flush()


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
