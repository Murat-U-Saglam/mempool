from mempool.stream.consumer.data_stream import consume
from mempool.config.settings import Settings
import asyncio


async def main():
    await consume(topic_name=Settings().KAFKA_TOPIC)


if __name__ == "__main__":
    asyncio.run(main())
