import asyncio
from mempool.stream.producer.data import log_loop
from mempool.config.provider import get_wss_provider, get_producer
from mempool.config.logging import setup_logger
from mempool.stream.producer.data import get_transactions_from_mempool
from mempool.stream.producer.topics import create_topic

logger = setup_logger(name="main_producer")


async def main():
    web3 = await get_wss_provider()
    events = await get_transactions_from_mempool(web3=web3)
    producer = await get_producer()
    topic_name = await create_topic(topic_name="transactions")
    try:
        await log_loop(
            event_filter=events, web3=web3, producer=producer, topic_name=topic_name
        )
    except Exception as e:
        logger.error(f"Error in main producer: {e} reason: {e}")
    finally:
        print("Closing filter")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except RuntimeError:
        asyncio.run(main())
