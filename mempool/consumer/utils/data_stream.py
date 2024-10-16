from mempool.config.logging import setup_logger
import asyncio
from mempool.config.access_config import get_deserializer, get_consumer
from confluent_kafka.serialization import SerializationContext, MessageField  # type: ignore
import pandas as pd
from mempool.consumer.utils.models import TransactionReceive
from typing import AsyncGenerator
from web3 import Web3
from collections import deque
import streamlit as st
from typing import List, Deque
from pydantic import ValidationError
import json
import time

logger = setup_logger(name="eth-transaction-consumer")


def update_data_buffer(
    buffer: Deque[TransactionReceive],
    new_data: List[TransactionReceive],
    max_size: int = 100,
) -> Deque[TransactionReceive]:
    """Pure function to update the data buffer"""
    new_buffer = deque(buffer, maxlen=max_size)
    new_buffer.extend(new_data)
    return new_buffer


"""
async def group_transaction(stream: AsyncGenerator[dict, None]):
    df_list = []
    async for transaction in stream:
        model = TransactionRecieve(**transaction)
        df_list.append(model.dict())
        df = pd.DataFrame(df_list)
        grouped = df.groupby("block_number")
        print("Current state of the data:")
        for block_number, group in grouped:
            print(f"Block number: {block_number}")
            analysed_group = await analyse_group(group)  # Yield it
            print(group)
            print("\n")
            return analysed_group
"""


def render_metrics(metrics: dict):
    st.write(metrics)


async def process_stream(
    generator: AsyncGenerator[List[TransactionReceive], None],
    buffer: Deque[TransactionReceive],
):
    try:
        async for transaction in generator:
            st.write(transaction)
            buffer.append(transaction)
            metrics = await analyse_group(transaction=transaction)
            st.write(metrics)
            render_metrics(metrics)
    except Exception as e:
        logger.error(f"Error in stream processing: {e}")
        st.error(f"Stream processing error: {e}")


async def get_data_stream(
    topic_name: str | None = None,
    max_retries: int = 3,
    retry_delay: float = 5.0,
    max_empty_messages: int = 100,
) -> AsyncGenerator[TransactionReceive, None]:
    if topic_name is None:
        logger.error("No topic name provided")
        return

    for attempt in range(max_retries):
        try:
            c = await get_consumer(topic_name=topic_name)
            c.subscribe([topic_name])
            deserialiser = await get_deserializer()
            empty_message_counter = 0

            while True:
                try:
                    message = c.poll(timeout=1.0)
                    
                    if message is None:
                        empty_message_counter += 1
                        if empty_message_counter > max_empty_messages:
                            logger.warning(f"Received {max_empty_messages} empty messages. Reconnecting...")
                            break
                        await asyncio.sleep(0.1)
                        continue

                    if message.error():
                        logger.error(f"Kafka message error: {message.error()}")
                        continue

                    transaction = deserialiser(
                        message.value(),
                        SerializationContext(message.topic(), field=MessageField.VALUE),
                    )
                    logger.debug(f"Consumed message {message.key()}: {message.value()}")
                    tx = TransactionReceive(**transaction)
                    yield tx
                    empty_message_counter = 0  # Reset counter on successful message

                except ValidationError as e:
                    logger.error(f"Validation error: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error processing message: {str(e)}")

        except Exception as e:
            logger.error(f"Error in Kafka consumer: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Exiting.")
                raise

        finally:
            try:
                c.close()
                logger.info("Kafka consumer closed.")
            except Exception as e:
                logger.error(f"Error closing Kafka consumer: {str(e)}")

    logger.info("Exiting get_data_stream")
        



def analyse_group(transaction: List[TransactionReceive]):
    st.write(transaction)
    transaction_df = [pd.DataFrame(t.dict()) for t in transaction]
    total_gas_price = calculate_total_gas_price(transaction_df)
    print(f"Total gas price: {total_gas_price}")
    return total_gas_price


def calculate_total_gas_price(group: pd.DataFrame):
    """
    Total gas price per block
    """
    total_gas_price = group["gas_price"].sum()  # In Gwei
    logger.info(f"Total gas price: {total_gas_price}")
    total_gas_price_in_eth = Web3.from_wei(int(total_gas_price), "ether")  # In ether
    logger.info(f"Total gas price in ether: {total_gas_price_in_eth}")
    dollar_value = 2000
    return (
        total_gas_price_in_eth * dollar_value
    )  # Assumes 1 ether = 2000 USD USE Api to get the current price


def group_to_and_from(group: pd.DataFrame):
    """
    Group by from and to
    """
    pass


def biggest_gas_spenders(group: pd.DataFrame):
    """
    Biggest gas spenders
    """
    grouped = group.groupby("from").agg(func={"gas": "sum", "gas_price": "sum"})
    pass


def biggest_senders(group: pd.DataFrame):
    """
    Biggest senders
    """
    pass


def biggest_receivers(group: pd.DataFrame):
    """
    Biggest receivers
    """
    pass
