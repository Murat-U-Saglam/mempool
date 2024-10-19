import streamlit as st
from mempool.consumer.utils.models import TransactionReceive
from mempool.config.access_config import Settings
from mempool.consumer.utils.data_stream import get_data_stream
from typing import List, Dict, Generator, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import StrEnum


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
    status: str = BlockStates.PENDING
    figure: Any = None


st.set_page_config("Mempool Analyser", ":chart_with_upwards_trend:", "wide")
if "current_block_data" not in st.session_state:
    st.session_state.current_block_data = BlockData()
if "historical_blocks" not in st.session_state:
    st.session_state.historical_blocks: Dict[int, BlockData] = {}
if "latest_block_number" not in st.session_state:
    st.session_state.latest_block_number = 0
if "current_view" not in st.session_state:
    st.session_state.current_view = "pending_block"
if "snapshot_buttons" not in st.session_state:
    st.session_state.snapshot_buttons = []

st.title("Mempool Analyser")
with st.sidebar:
    if st.button(":chart_with_upwards_trend: Pending Block"):
        st.session_state.current_view = "pending_block"
    st.sidebar.title("Histoical Blocks")
    for block_number in st.session_state.historical_blocks.keys():
        if st.button(f"Block {block_number}"):
            st.session_state.current_view = block_number

metrics_holder = st.empty()
historical_holder = st.sidebar.empty()


def update_current_metrics(tx: TransactionReceive):
    current_block = st.session_state.current_block_data
    current_block.transactions.append(tx)
    current_block.metrics.transaction_count += 1
    current_block.metrics.total_gas_used += tx.gas
    current_block.metrics.total_value_in_eth += tx.value
    current_block.metrics.average_gas_price = (
        current_block.metrics.total_gas_used / current_block.metrics.transaction_count
    )
    current_block.metrics.timestamp = datetime.now()
    st.session_state.current_block_data = current_block


def analyse_if_block_complete(tx: TransactionReceive):
    if (
        tx.block_number is not None
        and tx.block_number > st.session_state.latest_block_number
    ):
        st.session_state.latest_block_number = tx.block_number
        st.session_state.historical_blocks[tx.block_number] = (
            st.session_state.current_block_data
        )
        st.session_state.current_block_data = BlockData()
        return True


def create_button():
    new_block_number = st.session_state.latest_block_number
    if new_block_number not in st.session_state.snapshot_buttons:
        if st.sidebar.button(f"Block {new_block_number}"):
            st.session_state.current_view = new_block_number
            st.session_state.snapshot_buttons.append(new_block_number)


for tx in get_data_stream():
    update_current_metrics(tx)
    new_block = analyse_if_block_complete(tx)
    if new_block:
        create_button()
    if st.session_state.current_view == "pending_block":
        metrics_holder.write(st.session_state.current_block_data.metrics.dict())
    else:
        metrics_data = st.session_state.historical_blocks[
            st.session_state.current_view
        ].metrics
        metrics_holder.write(metrics_data.dict())
