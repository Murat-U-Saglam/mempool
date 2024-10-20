import streamlit as st
from pydantic import BaseModel, Field
from datetime import datetime
from mempool.consumer.utils.models import TransactionReceive
from mempool.config.access_config import Settings
from mempool.consumer.utils.data_stream import get_data_stream
from typing import List, Dict, Optional, Any, Union
from enum import StrEnum
import asyncio
import plotly.graph_objects as go
import time


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
    figure: Any = None
    status: str = BlockStates.PENDING


# Initialize session state
if "current_block_data" not in st.session_state:
    st.session_state.current_block_data = BlockData()
if "historical_blocks" not in st.session_state:
    st.session_state.historical_blocks = {}
if "latest_block_number" not in st.session_state:
    st.session_state.latest_block_number = 0
if "current_view" not in st.session_state:
    st.session_state.current_view = "pending_block"
if "snapshot_buttons" not in st.session_state:
    st.session_state.snapshot_buttons = []

st.set_page_config(
    page_title="Blockchain Analyser",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

st.title("Mempool analyser")

fig = go.Figure()
metrics_holder = st.empty()
historical_holder = st.sidebar.empty()

# Sidebar for navigation
st.sidebar.title("Navigation")
if st.sidebar.button(":chart_with_upwards_trend: Pending Block"):
    st.session_state.current_view = "pending_block"
    st.rerun()

st.sidebar.title(
    body=f"Currently viewing: {'Mempool' if st.session_state.current_view == 'pending_block' else st.session_state.current_view}"
)

st.sidebar.title(body="Historical Blocks")
for snapshot in st.session_state.snapshot_buttons:
    if st.sidebar.button(
        f":white_check_mark: Block Number {snapshot}", key=f"snapshot_{snapshot}"
    ):
        st.session_state.current_view = snapshot
        st.rerun()


def process_transaction(transaction: TransactionReceive) -> Optional[int]:
    st.session_state.current_block_data.transactions.append(transaction)
    _update_block_metrics(transaction)
    if (
        transaction.block_number is None
        or transaction.block_number <= st.session_state.latest_block_number
        or transaction.block_number == 0
    ):
        return None
    else:
        st.session_state.latest_block_number = transaction.block_number
        _save_current_block_data()
        add_snapshot_button_of_previous_block()
        return transaction.block_number


def _update_block_metrics(transaction: TransactionReceive):
    current_metrics = st.session_state.current_block_data.metrics
    current_metrics.transaction_count += 1
    current_metrics.total_gas_used += transaction.gas
    current_metrics.total_value_in_eth += transaction.value
    current_metrics.average_gas_price = (
        current_metrics.total_gas_used + transaction.gas_price
    ) / current_metrics.transaction_count
    current_metrics.timestamp = datetime.now()


def _save_current_block_data():
    st.session_state.current_block_data.status = BlockStates.COMPLETED
    st.session_state.historical_blocks[st.session_state.latest_block_number] = (
        st.session_state.current_block_data.copy()
    )
    st.session_state.current_block_data = BlockData()


def get_block_data(block_number: Union[int, str] = "pending_block") -> BlockData:
    if block_number == "pending_block" or block_number is None:
        return st.session_state.current_block_data
    return st.session_state.historical_blocks[int(block_number)]


def add_snapshot_button_of_previous_block():
    if st.session_state.latest_block_number not in st.session_state.snapshot_buttons:
        st.session_state.snapshot_buttons.append(st.session_state.latest_block_number)


def update_display(metrics: BlockMetric):
    metrics_holder.write(metrics.dict())


@st.cache_resource
def get_stream():
    return get_data_stream(topic_name=Settings().KAFKA_TOPIC)


def process_data_stream():
    for tx in get_stream():
        current_block_number = process_transaction(transaction=tx)

        block_data_to_display = get_block_data(
            block_number=st.session_state.current_view
        )
        current_metrics_for_block = block_data_to_display.metrics
        update_display(metrics=current_metrics_for_block)

        time.sleep(0.01)  # Small delay to prevent blocking

        if current_block_number is not None:
            st.rerun()


if "stream_processed" not in st.session_state:
    st.session_state.stream_processed = True
    process_data_stream()
