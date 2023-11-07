import requests
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy

w3 = Web3(Web3.HTTPProvider(
    'https://arb-mainnet.g.alchemy.com/v2/srwiQlBHZmQHVooKwYKQJjkIV52e5Ivz'))

w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
price = w3.eth.generate_gas_price()
print(w3.eth.max_priority_fee)
