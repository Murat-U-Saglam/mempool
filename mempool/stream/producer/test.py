from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Transaction(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel
    )
    block_hash: Optional[str] = None
    block_number: Optional[int] = None
    from_addres: str = Field(..., alias="from")
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
    y_parity: int

# Example input dictionary with snake_case field names
transaction_dict_snake_case = {
    'block_hash': '0x...',
    'block_number': 123456,
    'from': '0x...',
    'gas': 21000,
    'gas_price': 50,
    'hash': '0x...',
    'input': '0x...',
    'nonce': 1,
    'to': '0x...',
    'transaction_index': 0,
    'value': 100,
    'type': 2,
    'chain_id': 1,
    'v': 27,
    'r': '0x...',
    's': '0x...',
    'y_parity': 0
}

# Example input dictionary with camelCase field names
transaction_dict_camel_case = {
    'blockHash': '0x...',
    'blockNumber': 123456,
    'from': '0x...',
    'gas': 21000,
    'gasPrice': 50,
    'hash': '0x...',
    'input': '0x...',
    'nonce': 1,
    'to': '0x...',
    'transactionIndex': 0,
    'value': 100,
    'type': 2,
    'chainId': 1,
    'v': 27,
    'r': '0x...',
    's': '0x...',
    'yParity': 0
}

# Creating Transaction objects
#transaction_snake_case = Transaction(**transaction_dict_snake_case)
transaction_camel_case = Transaction(**transaction_dict_camel_case)

#print(transaction_snake_case)
print(transaction_camel_case)