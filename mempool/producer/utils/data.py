from web3.auto import Web3
import asyncio
from mempool.config.logging import setup_logger
from mempool.producer.utils.topics import send_transaction_to_kafka
from mempool.producer.utils.model import Transaction
from confluent_kafka import Producer  # type: ignore
from typing import Dict
from web3.exceptions import TransactionNotFound

logger = setup_logger(name="eth-transaction-producer")


async def clean_transaction(
    transaction_data: Dict[str, str | bytes | int],
) -> Transaction:
    logger.info(f"Cleaning transaction: {transaction_data}")
    transaction_dict = dict(transaction_data)
    hex_keys = ["hash", "input", "blockHash", "r", "s"]
    for key in hex_keys:
        if key in transaction_dict and isinstance(
            transaction_dict[key], bytes
        ):  ## linter is complaining about this line but we byte type checking here
            transaction_dict[key] = transaction_dict[key].hex()  # type: ignore
    transaction_data = Transaction(**transaction_dict)  # type: ignore # Make this permissive
    return transaction_data  # type: ignore


async def handle_event(
    event: Dict, web3: Web3, producer: Producer, topic_name: str, serialiser
) -> None:
    try:
        transaction = Web3.to_json(event).strip('"')
        try:
            transaction_data = await web3.eth.get_transaction(
                transaction_hash=transaction  # type: ignore
            )
        except TransactionNotFound:
            logger.error(
                f"Transaction not found: {transaction} -- TOO FAST FOR MEMPOOL"
            )
        cleaned_transaction = await clean_transaction(transaction_data)  # type: ignore
        await send_transaction_to_kafka(
            transaction_data=cleaned_transaction,
            topic_name=topic_name,
            producer=producer,
            serialiser=serialiser,
        )
    except Exception as e:
        logger.error(f"Error in handle_event: {e}")
        return None


async def get_transactions_from_mempool(web3):
    tx_filter = await web3.eth.filter("pending")
    return tx_filter


async def log_loop(
    event_filter, web3, producer, topic_name: str, serialiser, poll_interval=3
):
    while True:
        for event in await event_filter.get_new_entries():
            await handle_event(
                event=event,
                web3=web3,
                producer=producer,
                topic_name=topic_name,
                serialiser=serialiser,
            )
        await asyncio.sleep(delay=poll_interval)
