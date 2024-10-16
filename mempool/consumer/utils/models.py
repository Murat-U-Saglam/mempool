from pydantic import BaseModel
from typing import Optional, List, NamedTuple
from dataclasses import dataclass


@dataclass(frozen=True)
class StreamConfig:
    symbols: List[str]
    update_interval: float
    buffer_size: int
    volatility: float


class ChartConfig(NamedTuple):
    title: str
    height: int
    template: str


class TransactionReceive(BaseModel):
    block_hash: Optional[str] = None
    block_number: Optional[int] = None
    from_address: str
    input: Optional[str] = None
    gas: int
    gas_price: int
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    hash: str
    nonce: int
    to: Optional[str] = None
    transaction_index: Optional[int] = None
    value: int
    type: int
    chain_id: Optional[int] = None
    v: int
    r: str
    s: str
    y_parity: Optional[int] = None
