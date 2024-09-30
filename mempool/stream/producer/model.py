from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

def dual_case_alias(string: str) -> str:
    components = string.split('_')
    camel_case = components[0] + ''.join(x.title() for x in components[1:])
    
    return f"{camel_case}|{string}"

class Transaction(BaseModel):
    model_config = ConfigDict(
        alias_generator=dual_case_alias,
        populate_by_name=True
    )
    block_hash: Optional[str] = None
    block_number: Optional[int] = None
    from_address: str = Field(..., alias="from")
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
    yParity: Optional[int] = None
