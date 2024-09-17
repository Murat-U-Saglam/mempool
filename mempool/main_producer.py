import asyncio
from stream.producer.data import log_loop
from config.provider import get_wss_provider
from config.logging import setup_logger

logger = setup_logger(name="main_producer")

async def main():
    web3 = await get_wss_provider()
    try:
        await log_loop(
            web3=web3)
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
