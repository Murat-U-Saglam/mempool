from mempool.config.provider import get_consumer
from mempool.config.logging import setup_logger
import asyncio
from mempool.stream.consumer.utils import get_deserializer, group_transaction
from confluent_kafka.serialization import SerializationContext, MessageField # type: ignore

logger = setup_logger(name="eth-transaction-consumer")


async def consume(topic_name: str):
    c = await get_consumer(topic_name=topic_name)
    c.subscribe([topic_name])
    deserialiser = await get_deserializer()
    try:
        while True:
            message = c.poll(timeout=1.0)
            if message is None:
                continue
            elif message.error() is not None:
                logger.error(f"error: {message.error()}")
            else:
                transaction = deserialiser(message.value(), SerializationContext(message.topic(), MessageField.VALUE))
                logger.info(f"consumed message {message.key()}: {message.value()}")
                await group_transaction(transaction_data=transaction)
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        c.close()
