from mempool.config.provider import get_consumer
from mempool.config.logging import setup_logger
import asyncio
from mempool.stream.consumer.utils import get_deserializer
from confluent_kafka.serialization import SerializationContext, MessageField # type: ignore
import pandas as pd
from mempool.config.logging import setup_logger
from mempool.stream.producer.model import TransactionRecieve
from typing import AsyncGenerator, Dict
from web3 import Web3


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
        model = TransactionRecieve(**transaction)
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
    total_gas_price = await calculate_total_gas_price(group)
    print(f"Total gas price: {total_gas_price}")
    return total_gas_price

    
async def calculate_total_gas_price(group: pd.DataFrame):
    """
    Total gas price per block
    """
    total_gas_price = group["gas_price"].sum() # In Gwei
    logger.info(f"Total gas price: {total_gas_price}")
    total_gas_price_in_eth  = Web3.from_wei(int(total_gas_price), 'ether') # In ether
    logger.info(f"Total gas price in ether: {total_gas_price_in_eth}")
    dollar_value = 2000
    return total_gas_price_in_eth * dollar_value # Assumes 1 ether = 2000 USD USE Api to get the current price

async def group_to_and_from(group: pd.DataFrame):
    """
    Group by from and to
    """
    pass
    
    
async def biggest_gas_spenders(group: pd.DataFrame):
    """
    Biggest gas spenders
    """
    grouped = group.groupby('from').agg(func={'gas': 'sum', 'gas_price': 'sum'})
    pass
    
async def biggest_senders(group: pd.DataFrame):
    """
    Biggest senders
    """
    pass
    
async def biggest_receivers(group: pd.DataFrame):
    """
    Biggest receivers
    """
    pass
    
    
