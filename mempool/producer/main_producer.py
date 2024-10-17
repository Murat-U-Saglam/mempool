import asyncio
from mempool.producer.utils.data_stream import log_loop
from mempool.config.access_config import get_wss_provider, get_producer, get_serializer
from mempool.config.logging import setup_logger
from mempool.producer.utils.data_stream import get_transactions_from_mempool
from mempool.producer.utils.topics import create_topic


logger = setup_logger(name="main_producer")


async def main():
    web3 = await get_wss_provider()
    events = await get_transactions_from_mempool(web3=web3)
    producer = get_producer()
    serialiser = get_serializer()
    topic_name = await create_topic(topic_name="transactions")
    try:
        await log_loop(
            event_filter=events,
            web3=web3,
            producer=producer,
            topic_name=topic_name,
            serialiser=serialiser,
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
