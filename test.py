# working_iteration.py
import streamlit as st
import numpy as np
import time
from datetime import datetime
import asyncio
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class DataPoint:
    timestamp: datetime
    price: float
    volume: int


# Mock data generator to simulate yielded data
async def mock_data_generator():
    while True:
        timestamp = datetime.now()
        price = np.random.randint(100, 200) + np.random.random()
        volume = np.random.randint(1000, 10000)
        yield DataPoint(timestamp, price, volume)
        await asyncio.sleep(1)  # Simulate delay between data points


# Function to save snapshot
def save_snapshot(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.snapshots[timestamp] = data.copy()
    return timestamp


# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = []
if "snapshots" not in st.session_state:
    st.session_state.snapshots = {}
if "current_view" not in st.session_state:
    st.session_state.current_view = "Real-time Stream"
if "snapshot_buttons" not in st.session_state:
    st.session_state.snapshot_buttons = []

# Streamlit app
st.title("Data Stream with Snapshots")

# Sidebar for snapshots and navigation
st.sidebar.header("Snapshots and Navigation")
snapshot_interval = st.sidebar.slider("Snapshot Interval (seconds)", 5, 60, 30)

# Take snapshot button
if st.sidebar.button("Take Snapshot Now"):
    new_snapshot = save_snapshot(st.session_state.data)
    st.session_state.snapshot_buttons.append(new_snapshot)
    st.sidebar.success(f"Snapshot taken at {new_snapshot}")

# Real-time stream button
if st.sidebar.button("Return to Mempool Block"):
    st.session_state.current_view = "pending_block"

# Display current view
st.sidebar.write(f"Currently viewing: {st.session_state.current_view}")

# Snapshot navigation buttons
st.sidebar.header("Snapshot Navigation")
for timestamp in st.session_state.snapshot_buttons:
    if st.sidebar.button(f"View Snapshot: {timestamp}"):
        st.session_state.current_view = timestamp

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Data View")
    stream_placeholder = st.empty()

with col2:
    st.subheader("Summary Statistics")
    stats_placeholder = st.empty()

chart_placeholder = st.empty()


# Function to update display
def update_display(data):
    # Update stream display
    stream_placeholder.table(data[-10:])

    # Update summary statistics
    if data:
        prices = [d.price for d in data]
        volumes = [d.volume for d in data]
        stats = {
            "Price": {
                "mean": np.mean(prices),
                "std": np.std(prices),
                "min": np.min(prices),
                "max": np.max(prices),
            },
            "Volume": {
                "mean": np.mean(volumes),
                "std": np.std(volumes),
                "min": np.min(volumes),
                "max": np.max(volumes),
            },
        }
        stats_placeholder.table(stats)

    # Update chart
    if data:
        chart_data = {
            "Timestamp": [d.timestamp for d in data],
            "Price": [d.price for d in data],
        }
        chart_placeholder.line_chart(chart_data, x="Timestamp", y="Price")


# Async function to update data
async def update_data():
    async for new_data in mock_data_generator():
        if st.session_state.current_view == "Real-time Stream":
            # Append new data
            st.session_state.data.append(new_data)

            # Keep only the last 100 records
            st.session_state.data = st.session_state.data[-100:]

            # Update display with real-time data
            update_display(st.session_state.data)

            # Save snapshot if interval has passed
            if len(st.session_state.data) % snapshot_interval == 0:
                new_snapshot = save_snapshot(st.session_state.data)
                if new_snapshot not in st.session_state.snapshot_buttons:
                    st.session_state.snapshot_buttons.append(new_snapshot)
        else:
            # Display selected snapshot
            snapshot_data = st.session_state.snapshots[st.session_state.current_view]
            update_display(snapshot_data)

        # Use st.experimental_rerun() to update the UI and check for button presses
        st.rerun()


# Run the async function
if __name__ == "__main__":
    asyncio.run(update_data())
