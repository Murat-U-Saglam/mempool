import json
from web3.providers.persistent import WebSocketProvider
from web3 import AsyncWeb3
from mempool.config.settings import Settings
from mempool.config.logging import setup_logger
from confluent_kafka.schema_registry.schema_registry_client import SchemaRegistryClient  # type: ignore
from confluent_kafka import Producer, Consumer  # type: ignore
from confluent_kafka.admin import AdminClient  # type: ignore
from confluent_kafka.schema_registry import SchemaRegistryError  # type: ignore
from confluent_kafka.schema_registry.json_schema import JSONDeserializer, JSONSerializer  # type: ignore


logger = setup_logger(__name__)


async def get_wss_provider() -> AsyncWeb3:  # LegacyWebSocketProvider
    wss = Settings().WSS_URL
    web3 = await AsyncWeb3(WebSocketProvider(wss))
    assert await web3.is_connected(), "Failed to connect to web3 provider"
    logger.info(f"Connected to {wss}")
    return web3


async def get_producer() -> Producer:
    return Producer(
        {
            "bootstrap.servers": Settings().KAFKA_BROKER,
            "client.id": "eth-transaction-producer",
        }
    )


async def get_admin_client() -> AdminClient:
    return AdminClient({"bootstrap.servers": Settings().KAFKA_BROKER})


async def get_schema_registry() -> SchemaRegistryClient:
    return SchemaRegistryClient({"url": Settings().SCHEMA_REGISTRY_URL})


async def get_consumer(topic_name: str) -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": Settings().KAFKA_BROKER,
            "client.id": "eth-transaction-consumer",
            "group.id": "eth-transaction-group",
            "auto.offset.reset": "earliest",
        }
    )


async def get_schema() -> str:
    with open("/app/mempool/config/schema.json") as f:
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
        schema_str=json,
        schema_registry_client=schema_registry,
    )


async def get_deserializer():
    json = await get_schema()
    schema_registry = await get_schema_registry()
    return JSONDeserializer(
        schema_str=json, schema_registry_client=schema_registry
    )  # Convert schema to string
