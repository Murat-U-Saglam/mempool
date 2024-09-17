from web3.auto import Web3
from config.settings import Settings
from config.logging import setup_logger
from confluent_kafka import Producer

logger = setup_logger(__name__)

async def get_wss_provider() -> Web3.LegacyWebSocketProvider:
    wss = Settings().WSS_URL
    web3 = Web3(Web3.LegacyWebSocketProvider(wss))
    assert web3.is_connected(), "Failed to connect to web3 provider"
    logger.info(f"Connected to {wss}")
    return web3


async def get_producer():
    return Producer(
        {
            "bootstrap.servers": Settings().KAFKA_BROKER,
            "client.id": "eth-transaction-producer",
        }
    )