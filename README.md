{'blockHash': None, 'blockNumber': None, 'from': '0x17898f662F4392D6742Cbcc95bfb6495d8D38ECa', 'gas': 95090, 'gasPrice': 58363102332, 'maxFeePerGas': 58363102332, 'maxPriorityFeePerGas': 1000000000, 'hash': HexBytes('0xd0800d908e5b459859d56ce596b3a1d21a3af4185bbebe7314b53911e747adb8'), 'input': HexBytes('0x9aaab6482b8c9acc80c29b242728bffdf1b81986ceec6640a4128f0364117b557cb0291600000000000000000000000000000000000000000000000000000000008815805a43863a0513954cd54345a3d88e1045981df2c9bfebf345aa180602e5fffa21000000000000000000000000000000000000000000000000000000000066ed94'), 'nonce': 77274, 'to': '0x214F190b5B0e9697DF9Ab0303a86B7E886659fbc', 'transactionIndex': None, 'value': 0, 'type': 2, 'accessList': [], 'chainId': 11155111, 'v': 1, 'r': HexBytes('0xad37a7349b92621512aec22a1ccb00278765265294c2fd235af27505a8ac48a7'), 's': HexBytes('0x2098dcf0608b9ff07b12d394743244a8a0cc6d0ff3e7ac8a1d7829be60499535'), 'yParity': 1}

Group by to: and froms
Group total gas amount
total amount in assets - 20% stables - erc29 etc etc
total dollar amount
likelyhood in being in the next bock

group by block OBV
blockspace utilisiation

Etherscan achieves this by ordering all the transactions within that block by the gas price, if the order of the transaction (by index) does not match the order by the gas price (descending), the block contains private transactions.

And you could know the transactions that do not match the order are sent from private RPCs.

https://ethereum.stackexchange.com/a/134223/126666
