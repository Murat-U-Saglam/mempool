import streamlit as st
import asyncio
from mempool.consumer.utils.data_stream import get_data_stream, process_stream
from typing import Deque
from collections import deque
from mempool.consumer.utils.models import StreamConfig, ChartConfig, TransactionRecieve
from mempool.config.access_config import Settings


def initialize_app() -> tuple[StreamConfig, ChartConfig]:
    """Initialize the Streamlit application"""
    st.set_page_config(
        page_title="Mempool analyser",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("Mempool Transaction Analyser")
    
    stream_config = StreamConfig(
        symbols=['AAPL', 'GOOGL', 'MSFT', 'AMZN'],
        update_interval=1.0,
        buffer_size=100,
        volatility=0.001
    )
    
    chart_config = ChartConfig(
        title="Real-Time Stock Prices",
        height=600,
        template="plotly_dark"
    )
    
    return stream_config, chart_config

async def main():
    stream_config, chart_config = initialize_app()
    buffer: Deque[TransactionRecieve] = deque(maxlen=stream_config.buffer_size)
    st.session_state.running = True
    if st.session_state.running:
        data = get_data_stream(topic_name=Settings().KAFKA_TOPIC, buffer_size=stream_config.buffer_size)
        await process_stream(generator= data, buffer= buffer)

if __name__ == "__main__":
    asyncio.run(main())


