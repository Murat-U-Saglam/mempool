from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
from eth_pydantic_types import HashBytes32, HexBytes


class Transaction(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    block_hash: HexBytes | None
    block_number: int | None
    from_address: str = Field(..., alias="from")
    gas: int
    gas_price: int
    max_fee_per_gas: int
    max_priority_fee_per_gas: int
    hash: HexBytes   #TODO Create encodable type for hash
    input: HexBytes
    nonce: int
    to: str
    transactionIndex: int | None
    value: int
    type: int
    accessList: List = []
    chainId: int
    v: int
    r: HexBytes
    s: HexBytes
    yParity: int

    @field_validator("from_address")
    def check_from_address(cls, v):
        if not v.startswith("0x"):
            raise ValueError("Address must start with 0x")
        return v
