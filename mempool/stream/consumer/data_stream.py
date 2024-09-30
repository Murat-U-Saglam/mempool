from mempool.config.provider import get_consumer
from mempool.config.logging import setup_logger
import asyncio
from mempool.stream.consumer.utils import get_deserializer
from confluent_kafka.serialization import SerializationContext, MessageField # type: ignore
import pandas as pd
from mempool.config.logging import setup_logger
from mempool.stream.producer.model import Transaction
from typing import AsyncGenerator, Dict
import ast


logger = setup_logger(name="eth-transaction-consumer")


async def consume(c, deserialiser):
    try:
        while True:
            message = c.poll(timeout=1.0)
            if message is None:
                continue
            elif message.error() is not None:
                logger.error(f"error: {message.error()}")
            else:
                transaction = deserialiser(message.value(), SerializationContext(message.topic(), field=MessageField.VALUE))
                logger.info(f"consumed message {message.key()}: {message.value()}")
                yield transaction
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        c.close()

async def group_transaction(stream: AsyncGenerator[dict, None]):
    df_list = []
    async for transaction in stream:
        model = Transaction(**transaction)
        df_list.append(model.dict())
        df = pd.DataFrame(df_list)
        grouped = df.groupby('block_number')
        print("Current state of the data:")
        for block_number, group in grouped:
            print(f"Block number: {block_number}")
            analysed_group = await analyse_group(group) # Yield it
            print(group)
            print("\n")

async def main(topic_name: str):
    c = await get_consumer(topic_name=topic_name)
    c.subscribe([topic_name])
    deserialiser = await get_deserializer()
    stream = consume(c=c, deserialiser=deserialiser)
    await group_transaction(stream=stream)
    
async def analyse_group(group: pd.DataFrame):
    """
    All of this is per block information
    """
    total_gas_price = (group["gas_price"] * group["gas"]).sum() # In Gwei
    total_gas_price_in_dollars 
