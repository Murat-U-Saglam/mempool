from mempool.config.provider import get_consumer
from mempool.config.logging import setup_logger
import asyncio

logger = setup_logger(name="eth-transaction-consumer")


async def consume(topic_name: str):
    c = await get_consumer(topic_name)
    c.subscribe([topic_name])
    try:
        while True:
            message = c.poll(timeout=1.0)
            if message is None:
                logger.info("Waiting for message or event in poll()")
            elif message.error() is not None:
                logger.error(f"error: {message.error()}")
            else:
                logger.info(f"consumed message {message.key()}: {message.value()}")
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        c.close()
