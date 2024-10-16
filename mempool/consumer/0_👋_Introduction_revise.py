from pydantic import BaseModel, Field
from datetime import datetime
from mempool.consumer.utils.models import TransactionReceive
from mempool.consumer.utils.data_stream import get_data_stream
from mempool.config.access_config import Settings
from typing import List, Dict, Optional, Any, Union
from collections import defaultdict
import asyncio
import streamlit as st
import plotly.graph_objects as go  ## Importing plotly
from cachetools import TTLCache  ##ignore
import sys
from enum import StrEnum
import time

sys.setrecursionlimit(200000)


class BlockMetric(BaseModel):
    transaction_count: int = 0
    total_gas_used: int = 0
    total_value_in_eth: float = 0
    average_gas_price: float = 0
    timestamp: datetime = Field(default_factory=datetime.now)


class BlockStates(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


class BlockData(BaseModel):
    metrics: BlockMetric = BlockMetric()
    transactions: List[TransactionReceive] = []
    figure: Any = (
        None  ## Where the figure will go since figure types arent supported ATM
    )
    status: str = BlockStates.PENDING


class BlockchainAnalyser:
    def __init__(
        self,
        current_block_data: BlockData = BlockData(),
        historical_blocks: Dict[int, BlockData] = {},
        latest_block_number: int = 0,
    ):
        self.current_block_data: BlockData = BlockData()
        self.historical_blocks: Dict[int, BlockData] = {}
        self.latest_block_number: int = 0

    def process_transaction(self, transaction: TransactionReceive) -> Optional[int]:
        """
        Process a transaction and update the current block data
        if there is a new block it will save the current block data and update the latest block number
        """
        self.current_block_data.transactions.append(transaction)
        self._update_block_metrics(transaction=transaction)
        if (
            transaction.block_number is None
            or transaction.block_number <= self.latest_block_number
            or transaction.block_number == 0
        ):
            return None
        else:
            self.latest_block_number = transaction.block_number
            self._save_current_block_data()
            return transaction.block_number

    def _update_block_metrics(self, transaction: TransactionReceive):
        current_metrics = self.current_block_data.metrics
        current_metrics.transaction_count += 1
        current_metrics.total_gas_used = (
            current_metrics.total_gas_used + transaction.gas
        )
        current_metrics.total_value_in_eth = (
            current_metrics.total_value_in_eth + transaction.value
        )
        current_metrics.average_gas_price = (
            current_metrics.total_gas_used + transaction.gas_price
        ) / current_metrics.transaction_count
        current_metrics.timestamp = datetime.now()

    def _save_current_block_data(self):
        self.current_block_data.status = BlockStates.COMPLETED
        self.historical_blocks[self.latest_block_number] = self.current_block_data
        self.current_block_data = BlockData()

    def get_block_data(
        self, block_number: Union[int, str] = "pending_block"
    ) -> BlockData:
        if block_number == "pending_block":
            return self.current_block_data
        return self.historical_blocks[int(block_number)]


def update_session_state(key, value):
    state = value


async def update_side_bar(container, block_number: int, analyser: BlockchainAnalyser):
    with container:
        if st.sidebar.button(
            label=f":white_check_mark: Block Number {block_number}",
            key=f"{block_number}",
            on_click=update_session_state,
            args=["selected_block", block_number],
        ):
            pass


async def main():
    st.set_page_config(
        page_title="Blockchain Analyser",
        page_icon=":chart_with_upwards_trend:",
        layout="wide",
    )
    # if "selected_block" not in st.session_state:
    #    state = "pending_block"
    st.title("Mempool analyser")
    global state
    state = "pending_block"

    chart = st.empty()
    fig = go.Figure()
    chart.plotly_chart(figure_or_data=fig, use_container_width=True)
    analyser = BlockchainAnalyser()
    metrics_holder = st.empty()
    running = st.sidebar.checkbox(label="Start/Stop", value=True)

    historical_holder = st.sidebar.empty()
    st.sidebar.button(
        label=":chart_with_upwards_trend: Pending Block",
        key="pending_block",
        on_click=update_session_state,
        args=["selected_block", "pending_block"],
    )
    st.sidebar.title("Historical Blocks")
    sleep_duration = 0.01
    st.write(state)
    try:
        async for tx in get_data_stream(topic_name=Settings().KAFKA_TOPIC):
            if not running:
                await asyncio.sleep(sleep_duration)
                continue
            current_block_number = analyser.process_transaction(transaction=tx)

            block_to_display = state or "pending_block"
            block_data_to_display = analyser.get_block_data(
                block_number=block_to_display
            )
            ## Update the chart
            current_metrics_for_block = block_data_to_display.metrics
            metrics_holder.markdown(
                body=f"""### Block Metrics
                - Transaction Count: {current_metrics_for_block.transaction_count}
                - Total Gas Used: {current_metrics_for_block.total_gas_used}
                - Total Value: {current_metrics_for_block.total_value_in_eth}
                - Average Gas Price: {current_metrics_for_block.average_gas_price}
                - Timestamp: {current_metrics_for_block.timestamp}
            """
            )
            if current_block_number is not None:
                await update_side_bar(
                    container=historical_holder,
                    analyser=analyser,
                    block_number=analyser.latest_block_number,
                )

            await asyncio.sleep(sleep_duration)
    except Exception as e:
        st.error(f"An error occured: {e}")
        st.stop()


if __name__ == "__main__":
    asyncio.run(main())
