import json
import requests
from web3 import Web3
import eth_abi
import time

# Connect to an Arbitrum node
w3 = Web3(Web3.HTTPProvider(
    'https://arb-mainnet.g.alchemy.com/v2/srwiQlBHZmQHVooKwYKQJjkIV52e5Ivz'))

url = "https://tiniest-broken-flower.arbitrum-mainnet.quiknode.pro/d951fac1b2bd031bee2eeb97a0c754b8155a4d8c/"


function_signature = "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)"

function_selector = Web3.keccak(text=function_signature)[:4].hex()

# Encode the parameters using eth_abi and convert to hex
encoded_parameters = eth_abi.encode(
    types=("uint256", "uint256", "address[]", "address", "uint256"),
    args=(
        int(219),
        int(217),
        [
            Web3.to_checksum_address(
                '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'),
            Web3.to_checksum_address(
                '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'),
            Web3.to_checksum_address(
                '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8')
        ],
        Web3.to_checksum_address('0x80B266c55cAef51856C9051963DA844814FC547d'),
        int(time.time() + 180)
    )
).hex()

# # Concatenate function selector and parameters
data = function_selector + encoded_parameters
print(data)
payload_data = {
    "method": "eth_estimateGas",
    "params": [
        {
            "to": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
            "data": data,
            "value": "0x0"
        }
    ],
    "id": 1,
    "jsonrpc": "2.0"
}
payload = json.dumps(payload_data)
headers = {
    'Content-Type': 'application/json'
}


# # Define the transaction for which you want to estimate gas
# transaction = {
#     'to': '0x...',  # The address you are sending to
#     'data': data,  # Data to send, if any
# }

# transaction = {
#     'to': '0xRecipientAddress',
#     'value': w3.toWei(1, 'ether'),
#     'data': '0x...',
#     # 'from': '0xYourAddress',  # Optionally add this if you want a more accurate estimate
#     # You might need to add other fields depending on the transaction type
# }

# # Estimate gas limit
# gas_limit = w3.eth.estimate_gas(transaction)  # type: ignore

# # Get current base fee from the latest block
# latest_block = w3.eth.get_block('latest')
# base_fee = latest_block['baseFeePerGas']  # type: ignore

# # Define a priority fee (tip) - this is up to you
# priority_fee = w3.to_wei(2, 'gwei')  # type: ignore

# # Calculate total gas price
# total_gas_price = base_fee + priority_fee

# # Calculate max fee for the transaction
# max_fee = gas_limit * total_gas_price

# print(f"Estimated gas limit: {gas_limit}")
# print(f"Current base fee: {w3.from_wei(base_fee, 'gwei')} gwei")
# print(f"Priority fee: {w3.from_wei(priority_fee, 'gwei')} gwei")
# print(f"Total gas price: {w3.from_wei(total_gas_price, 'gwei')} gwei")
# print(f"Maximum fee for transaction: {w3.from_wei(max_fee, 'ether')} Ether")


response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
