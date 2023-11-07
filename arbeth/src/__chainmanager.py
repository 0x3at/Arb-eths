from decimal import Decimal
from dotenv import load_dotenv, find_dotenv
from os import environ
import json

from web3 import Web3  # // Link to docs: https://shorturl.at/agMQX // #
from eth_account import Account  # // Link to docs: https://shorturl.at/sHW39 // #
from eth_account.signers.local import LocalAccount
from eth_typing import (  # // Link to docs: https://shorturl.at/cBJ28 // #
    ChecksumAddress,
    TypeStr,
)
load_dotenv(find_dotenv())
W3 = Web3(Web3.HTTPProvider(
    'https://arb-mainnet.g.alchemy.com/v2/srwiQlBHZmQHVooKwYKQJjkIV52e5Ivz'))

WETH = Web3.to_checksum_address("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1")
ORACLE = Web3.to_checksum_address("0x639fe6ab55c921f74e7fac1ee960c0b6293ba612")
# Initialize ABIs in the base class
with open(environ.get("PATH_TO_ERC_ABI")) as erc20ABI:  # type: ignore
    erc_20_ABI = json.load(erc20ABI)
with open(environ.get("PATH_TO_UNI_LP_ABI")) as uniLPABI:  # type: ignore
    uni_lp_ABI = json.load(uniLPABI)
with open(environ.get("PATH_TO_UNI_FACT_ABI")) as uniFactABI:  # type: ignore
    uni_fact_ABI = json.load(uniFactABI)
with open(environ.get("PATH_TO_SUSHI_ROUTER_ABI")) as sushiRoutAbi:  # type: ignore
    sushi_rout_ABI = json.load(sushiRoutAbi)
with open(environ.get("PATH_TO_ORACLE_ABI")) as oracleABI:  # type: ignore
    oracle_ABI = json.load(oracleABI)


class ChainManager:
    def __init__(
        self,
        W3: Web3 = W3,
        wethAddress: ChecksumAddress = WETH,
        oracleAddress: ChecksumAddress = ORACLE,
        erc20ABI: TypeStr = erc_20_ABI,
        oracleABI: TypeStr = oracle_ABI,
        publickey: ChecksumAddress = environ.get("PUBLIC_KEY"),  # type: ignore
    ) -> None:
        # -- Initialize Web 3 Cursor Object
        self.w3 = W3
        # -- Chain Data
        self.blockNumber = self.w3.eth.block_number
        self.chainID = self.w3.eth.chain_id

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

        self.weth = self.w3.eth.contract(
            address=self.wethAddress, abi=self.erc20ABI)

        self.transaction: dict = {
            "chainId": self.chainID,
            "from": publickey,
            "nonce": self.w3.eth.get_transaction_count(publickey),
            "gas": self.gasPrice,
            "maxFeePerGas": self.maxFeePerGas,
            "maxPriorityFeePerGas": self.gasPriorityFee
        }

    @property
    def gasPrice(self):
        return self.w3.eth.gas_price

    @property
    def gasPriorityFee(self):
        return self.w3.eth.max_priority_fee

    @property
    def maxFeePerGas(self):
        return self.gasPrice

    def to_readable_value(self, wei: int, decimal: int) -> Decimal:
        return Decimal(wei / 10**decimal)  # type: ignore

    def to_raw_value(self, eth: Decimal, decimal: int) -> int:
        return int(eth * 10**decimal)  # type: ignore

    def convert_gwei_to_wei(self, gwei: int) -> Decimal:
        return Decimal(gwei * (10**9))

    def convert_gwei_to_eth(self, gwei: int) -> Decimal:
        return Decimal(gwei * (10**9) / 10**18)

    def convert_eth_to_usd(self, eth) -> Decimal:
        return Decimal(
            eth
            * self.to_readable_value(
                self.ETH_USD_oracle.functions.latestAnswer().call(),
                self.ETH_USD_oracle.functions.decimals().call(),
            )
        )

    def retrieve_current_ETH_price(self) -> Decimal:
        return Decimal(self.ETH_USD_oracle.functions.latestAnswer().call()) / (
            10 ** self.ETH_USD_oracle.functions.decimals().call()
        )

    def get_gas_price_in_gwei(self, transaction=None) -> int:
        if transaction is None:
            transaction = self.transaction
        est_gas_in_gwei = self.w3.eth.estimate_gas(transaction)  # type: ignore
        return int(est_gas_in_gwei)

    def get_gas_price_in_USD(self, transaction=None) -> Decimal:
        if transaction is None:
            transaction = self.transaction
        est_gas_in_gwei = self.w3.eth.estimate_gas(transaction)  # type: ignore
        est_gas_in_eth = self.convert_gwei_to_eth(est_gas_in_gwei)
        return self.convert_eth_to_usd(est_gas_in_eth)
