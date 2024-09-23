from web3.auto import Web3
from mempool.config.settings import Settings
from mempool.config.logging import setup_logger
from confluent_kafka.schema_registry.schema_registry_client import SchemaRegistryClient
from confluent_kafka import Producer, Consumer  # type: ignore
from confluent_kafka.admin import AdminClient

logger = setup_logger(__name__)


async def get_wss_provider() -> Web3:  # LegacyWebSocketProvider
    wss = Settings().WSS_URL
    web3 = Web3(Web3.LegacyWebSocketProvider(wss, websocket_timeout=60))
    assert web3.is_connected(), "Failed to connect to web3 provider"
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
            "group.id": Settings().KAFKA_GROUP,
            "auto.offset.reset": "earliest",
        }
    )
