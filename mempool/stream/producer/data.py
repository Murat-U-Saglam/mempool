from web3.auto import Web3
from web3.datastructures import AttributeDict
import asyncio
from config.provider import get_producer
from config.settings import Settings
from config.logging import setup_logger

logger = setup_logger(name="eth-transaction-producer")

async def handle_event(event, web3) -> AttributeDict:
    transaction = Web3.to_json(event).strip('"')
    transaction_data = web3.eth.get_transaction(transaction)
    return transaction_data


async def get_transactions_from_mempool(web3):
    tx_filter = web3.eth.filter("pending")
    return tx_filter




async def log_loop(web3, poll_interval = 3):
    producer = await get_producer()
    events = await get_transactions_from_mempool(web3)
    while True:
        for event in events.get_new_entries():
            data = await handle_event(event, web3=web3)
            producer.produce(
                Settings().KAFKA_TOPIC,
                key=data["hash"].hex(),
                value=str(data),
                callback=delivery_report,
                
            )
            logger.info(f"Sent transaction: {data['hash'].hex() } - {data['from']} -> {data['to']}")
        await asyncio.sleep(poll_interval)


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")