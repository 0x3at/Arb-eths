import json
from dotenv import load_dotenv
from os import getenv
from decimal import Decimal
import time

from web3 import Web3  # // Link to docs: https://shorturl.at/agMQX // #
from eth_account import Account  # // Link to docs: https://shorturl.at/sHW39 // #
from eth_account.signers.local import LocalAccount
from eth_typing import (  # // Link to docs: https://shorturl.at/cBJ28 // #
    ChecksumAddress,
    TypeStr,
)

from _transactionC import TransactionC


class ChainManager:
    def __init__(
        self,
        wethAddress: ChecksumAddress,
        oracleAddress: ChecksumAddress,
        erc20ABI: TypeStr,
        oracleABI: TypeStr,
        W3: Web3,
        address: ChecksumAddress,
    ) -> None:
        # -- Initialize Web 3 Cursor Object
        self.w3 = W3

        # -- Chain Data
        self.blockNumber = self.w3.eth.block_number
        self.chainID = self.w3.eth.chain_id
        self.gasPrice = self.w3.eth.gas_price
        self.maxFeePerGas = self.gasPrice
        self.gasPriorityFee = self.w3.eth.max_priority_fee

        # -- ABI's
        self.erc20ABI: TypeStr = erc20ABI
        self.oracleABI: TypeStr = oracleABI

        # -- Addresses
        self.wethAddress: ChecksumAddress = wethAddress
        self.ETH_USD_oracleAddress: ChecksumAddress = oracleAddress

        # -- Contracts
        self.ETH_USD_oracle = self.w3.eth.contract(
            address=self.ETH_USD_oracleAddress, abi=self.oracleABI
        )

        self.weth = self.w3.eth.contract(address=self.wethAddress, abi=self.erc20ABI)

        # -- Prebuilt Transaction Object
        self.transaction = TransactionC(
            chainId=self.chainID,
            nonce=self.w3.eth.get_transaction_count(address),
            gas=self.gasPrice,
            maxFeePerGas=self.maxFeePerGas,
            maxPriorityFeePerGas=self.gasPriorityFee,
        )

        # --  Methods

    def to_readable_value(self, value: int, decimal: int) -> Decimal:
        return Decimal(value) / 10**decimal  # type: ignore

    def to_raw_value(self, value: Decimal, decimal: int) -> int:
        return int(value * 10**decimal)  # type: ignore

    def convert_gwei_to_wei(self, gwei: int) -> Decimal:
        return Decimal(gwei * (10**9))

    def convert_gwei_to_eth(self, gwei: int) -> Decimal:
        return Decimal(gwei * (10**9) / 10**18)

    def convert_eth_to_usd(self, eth) -> Decimal:
        return Decimal(eth * self.ETH_USD_oracle.functions.latestAnswer().call())

    def retrieve_current_ETH_price(self) -> Decimal:
        return Decimal(self.ETH_USD_oracle.functions.latestAnswer().call()) / (
            10 ** self.ETH_USD_oracle.functions.decimals().call()
        )  # type: ignore

    def retrieve_transaction_dict(self) -> dict:
        transaction = {
            "chainId": self.transaction.chainId,
            "nonce": self.transaction.nonce,
            "gas": self.transaction.gas,
            "maxFeePerGas": self.transaction.maxFeePerGas,
            "maxPriorityFeePerGas": self.transaction.maxPriorityFeePerGas,
        }
        return transaction

    def estimate_gas_in_gwei(self, transaction: dict) -> int:
        return self.w3.eth.estimate_gas(transaction)  # type: ignore

    def get_gas_price_in_USD(self, transaction: dict) -> Decimal:
        est_gas_in_gwei = self.w3.eth.estimate_gas(transaction)  # type: ignore
        est_gas_in_eth = self.convert_gwei_to_eth(est_gas_in_gwei)
        return self.convert_eth_to_usd(est_gas_in_eth)

    def wait_for_transaction_receipt(self, transaction_hash: str):
        return self.w3.eth.wait_for_transaction_receipt(transaction_hash)  # type: ignore
