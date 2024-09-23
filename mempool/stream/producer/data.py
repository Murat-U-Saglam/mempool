from web3.auto import Web3
import asyncio
from mempool.config.logging import setup_logger
from mempool.stream.producer.topics import create_topic, send_transaction_to_kafka
from mempool.stream.producer.model import Transaction

logger = setup_logger(name="eth-transaction-producer")


async def handle_event(event, web3, producer) -> None:
    try:
        transaction = Web3.to_json(event).strip('"')
        transaction_data = web3.eth.get_transaction(transaction)
        transaction_dict = dict(transaction_data)
        transaction_data = Transaction(**transaction_dict)
        topic_name = await create_topic(topic_name="transactions")
        logger.info(
            f"Sending transaction to Kafka: {transaction_dict} - {transaction_data}"
        )
        await send_transaction_to_kafka(
            transaction_data=transaction_data, topic_name=topic_name, producer=producer
        )
    except Exception as e:
        logger.error(f"Error in handle_event: {e}")
        return None


async def get_transactions_from_mempool(web3):
    tx_filter = web3.eth.filter("pending")
    return tx_filter


async def log_loop(event_filter, web3, producer, poll_interval=3):
    while True:
        for event in event_filter.get_new_entries():
            await handle_event(event=event, web3=web3, producer=producer)
        await asyncio.sleep(delay=poll_interval)
