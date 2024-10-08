from mempool.consumer.utils.data_stream import main as consooomer
from mempool.config.settings import Settings
import asyncio


async def main():
    await consooomer(Settings().KAFKA_TOPIC)


if __name__ == "__main__":
    asyncio.run(main())
