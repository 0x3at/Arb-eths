from decimal import Decimal

from web3 import Web3
from eth_typing import (
    ChecksumAddress,
    TypeStr
)


class ChainTools:
    def __init__(
            self,
            settings,  # ! Make Base Network Class
            W3: Web3

    ) -> None:
        self.w3 = W3
        self.public_key = settings.public_key
        self.block_number = self.w3.eth.chain_id

        self.chain_id = self.w3.eth.chain_id
        #! Turn inro attribute methods

        @property
        def gas_price(self) -> int:
            return self.w3.eth.gas_price

        @property
        def max_fee(self) -> int:
            return gas_price + 1  # type: ignore
        self.w3.eth.max_priority_fee

        @property
        def priority_fee(self) -> int:
            return self.w3.eth.max_priority_fee  # type: ignore

        # -- ABI's
        self.erc_abi: TypeStr = settings.erc_20_ABI
        self.oracle_abi: TypeStr = settings.oracle_ABI

        self.weth_address: ChecksumAddress = self.w3.to_checksum_address(
            settings.weth)
        self.eth_usd_oracle_address: ChecksumAddress = self.w3.to_checksum_address(
            settings.oracle)

        # -- Contracts
        self.eth_usd_oracle_contract = self.w3.eth.contract(
            address=self.eth_usd_oracle_address, abi=self.oracle_abi
        )
        self.weth = self.w3.eth.contract(
            address=self.weth_address, abi=self.erc_abi)

        self.transaction_dict = {
            "chainId": self.chain_id,
            "nonce": W3.eth.get_transaction_count(self.public_key),
            "gas": gas_price,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee,
        }

    # --  Methods

    def to_readable_value(self, wei: int, decimal: int) -> Decimal:
        return Decimal(wei) / 10**decimal  # type: ignore

    def to_raw_value(self, eth: Decimal, decimal: int) -> int:
        return int(eth * 10**decimal)  # type: ignore

    def convert_gwei_to_wei(self, gwei: int) -> Decimal:
        return Decimal(gwei * (10**9))

    def convert_gwei_to_eth(self, gwei: int) -> Decimal:
        return Decimal(gwei * (10**9) / 10**18)

    def convert_eth_to_usd(self, eth) -> Decimal:
        return Decimal(eth * self.eth_usd_oracle_contract.functions.latestAnswer().call())

    def retrieve_current_ETH_price(self) -> Decimal:
        return Decimal(self.eth_usd_oracle_contract.functions.latestAnswer().call()) / (
            10 ** self.eth_usd_oracle_contract.functions.decimals().call()
        )

    def estimate_gas_in_gwei(self, transaction: dict) -> int:
        return self.w3.eth.estimate_gas(transaction)  # type: ignore

    def get_gas_price_in_USD(self, transaction: dict | None) -> Decimal:
        if transaction is None:
            transaction = self.transaction_dict
        est_gas_in_gwei = self.w3.eth.estimate_gas(transaction)  # type: ignore
        est_gas_in_eth = self.convert_gwei_to_eth(est_gas_in_gwei)
        return self.convert_eth_to_usd(est_gas_in_eth)
