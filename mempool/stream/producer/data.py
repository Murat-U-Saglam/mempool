from web3.auto import Web3
import asyncio
from mempool.config.provider import get_producer
from mempool.config.settings import Settings
from mempool.config.logging import setup_logger

logger = setup_logger(name="eth-transaction-producer")


async def handle_event(event, web3) -> None:
    producer = await get_producer()
    try:
        transaction = Web3.to_json(event).strip('"')
        transaction_data = web3.eth.get_transaction(transaction)
        producer.produce(
            Settings().KAFKA_TOPIC,
            key=transaction_data["hash"].hex(),
            value=str(transaction_data),
            callback=delivery_report,
        )
        logger.info(
            f"Sent transaction: {transaction_data['hash'].hex() } - {transaction_data['from']} -> {transaction_data['to']}"
        )
        producer.flush()
    except Exception as e:
        logger.error(f"Error in handle_event: {e}")
        return None


async def get_transactions_from_mempool(web3):
    tx_filter = web3.eth.filter("pending")
    return tx_filter


async def log_loop(event_filter, web3, poll_interval=3):
    while True:
        for event in event_filter.get_new_entries():
            await handle_event(event, web3=web3)

        await asyncio.sleep(poll_interval)


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
