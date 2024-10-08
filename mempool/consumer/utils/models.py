from pydantic import BaseModel
from typing import Optional


class TransactionRecieve(BaseModel):
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
    to: str
    transaction_index: Optional[int] = None
    value: int
    type: int
    chain_id: int
    v: int
    r: str
    s: str
    y_parity: Optional[int] = None
