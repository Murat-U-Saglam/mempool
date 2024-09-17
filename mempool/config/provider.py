from web3.auto import Web3
from mempool.config.settings import Settings
from mempool.config.logging import setup_logger
from confluent_kafka import Producer, Consumer  # type: ignore

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


async def get_consumer(topic_name: str) -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": Settings().KAFKA_BROKER,
            "group.id": Settings().KAFKA_GROUP,
            "auto.offset.reset": "earliest",
        }
    )
