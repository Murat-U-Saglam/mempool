from web3.providers.persistent import WebSocketProvider
from web3 import Web3
from web3 import AsyncWeb3
from mempool.config.settings import Settings
from mempool.config.logging import setup_logger
from confluent_kafka.schema_registry.schema_registry_client import SchemaRegistryClient # type: ignore
from confluent_kafka import Producer, Consumer  # type: ignore
from confluent_kafka.admin import AdminClient # type: ignore

logger = setup_logger(__name__)


async def get_wss_provider() -> AsyncWeb3:  # LegacyWebSocketProvider
    wss = Settings().WSS_URL
    web3 = AsyncWeb3(WebSocketProvider(wss, websocket_timeout=300))
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
            "client.id": "eth-transaction-consumer",
            "group.id": "eth-transaction-group",
            "auto.offset.reset": "earliest",
        }
    )
