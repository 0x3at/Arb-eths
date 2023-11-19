from decimal import Decimal
from time import time

from web3 import (
    Web3,
    exceptions  # // Link to docs: https://shorturl.at/agMQX // #
)
from eth_account import Account
from eth_typing import (  # // Link to docs: https://shorturl.at/cBJ28 // #
    ChecksumAddress,
    TypeStr,
)
# -- Local Imports
from arbeth.src2.__settings import *
from arbeth.src2.__ChainTools import ChainTools

# -- Global Variables
SETTINGS_BUFFER = SettingsBuffer(network_index=0).config  # type: ignore
W3: Web3 = Web3(Web3.HTTPProvider(SETTINGS_BUFFER.api))
PRIVATE_KEY = Web3.to_checksum_address(SETTINGS_BUFFER.private_key)
PUBLIC_KEY = Web3.to_checksum_address(SETTINGS_BUFFER.public_key)
CHAIN_TOOLS = ChainTools(settings=SETTINGS_BUFFER, W3=W3)
WETHADDRESS = Web3.to_checksum_address(SETTINGS_BUFFER.weth)


# -- Functional Stablecoin Class
class StableCoin:
    def __init__(self, address: str):
        self.address: ChecksumAddress = Web3.to_checksum_address(address)

        self.contract = W3.eth.contract(
            address=self.address, abi=SETTINGS_BUFFER.erc_20_ABI)

        self.name: str = self.contract.functions.name().call()
        self.symbol: str = self.contract.functions.symbol().call()
        self.decimals: int = self.contract.functions.decimals().call()
        self.readable_balance: Decimal = (
            Decimal(self.contract.functions.balanceOf(
                PUBLIC_KEY).call()) / 10**self.decimals
        )
        self.raw_balance: int = self.contract.functions.balanceOf(
            PUBLIC_KEY)  # type: ignore

    # -- Methods
    def getAllowance(self, spender: ChecksumAddress):
        return self.contract.functions.allowance(PUBLIC_KEY, spender).call()

    def approve(self, spender: ChecksumAddress, amount: Decimal):
        if self.getAllowance(spender) >= CHAIN_TOOLS.to_raw_value(
            amount, self.decimals
        ):
            return True

        else:
            # ! Finish class method on chaintools
            transaction = CHAIN_TOOLS.transaction_dict

            builtTransaction = self.contract.functions.approve(
                spender, CHAIN_TOOLS.to_raw_value(amount, self.decimals)
            ).build_transaction(
                transaction  # type: ignore
            )

            signedTX = W3.eth.account.sign_transaction(
                builtTransaction, PRIVATE_KEY)
            if Web3.to_hex(
                W3.eth.send_raw_transaction(
                    transaction=signedTX.rawTransaction)
            ):
                return True
            else:
                print("Error during approve contract call")
                return False


# --  Singleton User Class
class User:

    _instance = None

    def __new__(cls, token0: StableCoin | None = None, token1: StableCoin | None = None):
        if cls._instance is None:
            cls._instance = super(User, cls).__new__(cls)
            cls._instance.initialize(token0, token1)
        return cls._instance

    def initialize(self, token0, token1):
        self.account: Account = Account.from_key(PRIVATE_KEY)
        self.address: ChecksumAddress = PUBLIC_KEY
        self.nonce: int = W3.eth.get_transaction_count(self.address)
        self.key = self.account.key  # type: ignore
        self.token0 = token0
        self.token1 = token1


# -- Functional DEX Class for V2 & V2 clones
class V2Dex:
    def __init__(self, dex_name: str, router_address: str, factory_address: str, user: User):
        self.name = dex_name
        self.user = user

        # addresses
        self.__oracle_address: ChecksumAddress = Web3.to_checksum_address(
            SETTINGS_BUFFER.oracle)
        self.__router_address: ChecksumAddress = Web3.to_checksum_address(
            router_address)
        self.__factory_address: ChecksumAddress = Web3.to_checksum_address(
            factory_address)

        # Contracts
        self.router_contract = W3.eth.contract(
            address=self.__router_address, abi=TypeStr(SETTINGS_BUFFER.sushi_rout_ABI))
        self.factory_contract = W3.eth.contract(
            address=self.__factory_address, abi=TypeStr(SETTINGS_BUFFER.uni_fact_ABI))
        self.oracle_contract = W3.eth.contract(
            address=self.__oracle_address, abi=TypeStr(SETTINGS_BUFFER.oracle_ABI))

    def get_amounts_out(self, amount_in: int, path: list):
        return self.router_contract.functions.getAmountsOut(amount_in, path).call()

    def execute_router_exact_tokens_for_tokens(
        self, amountIn: int, path: list, amountOutMin: int
    ):
        transaction = CHAIN_TOOLS.transaction_dict

        built_transaction = self.router_contract.functions.swapExactTokensForTokens(
            amountIn, amountOutMin, path, PUBLIC_KEY, int(time() + 60)
        ).build_transaction(
            transaction  # type: ignore
        )
        signedTX = W3.eth.account.sign_transaction(
            built_transaction, PRIVATE_KEY)

        tx_hash = W3.eth.send_raw_transaction(
            transaction=signedTX.rawTransaction)
        try:
            tx_receipt = W3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=120)
            print("Transaction Successful\n")
            print(tx_receipt)
            return True
        except exceptions.TimeExhausted:
            print("Transaction Timed Out")
            return False

    def scan_for_arbitrage(self):
        transaction_cost = CHAIN_TOOLS.get_gas_price_in_USD(
            None) - Decimal(0.1)

        print(f"Estimated TX Cost: ${transaction_cost}\n")

        path: list = [self.user.token0.address,
                      WETHADDRESS, self.user.token1.address]
        min_recieved = self.get_amounts_out(self.user.token0.raw_balance, path)

        print(
            f"""
====================================================================|
Starting Path:\n
Out: {self.user.token0.symbol} : {self.user.token0.readable_balance}\n
In:  {self.user.token1.symbol} : {CHAIN_TOOLS.to_readable_value(min_recieved,self.user.token1.decimals)}\n
- Potential Profit: {CHAIN_TOOLS.to_readable_value(min_recieved,self.user.token1.decimals)-Decimal(self.user.token0.readable_balance + transaction_cost)}\n
====================================================================|\n
"""
        )

        if self.user.token0.readable_balance > 1:
            if (
                CHAIN_TOOLS.to_readable_value(
                    min_recieved, self.user.token1.decimals)
                > self.user.token0.readable_balance + transaction_cost
            ):
                print("Arbitrage Opportunity Found!")

                if self.user.token0.approve(
                    self.__router_address, self.user.token0.readable_balance
                ):
                    self.execute_router_exact_tokens_for_tokens(
                        self.user.token0.raw_balance, path, min_recieved
                    )
                    return True

        if self.user.token1.readable_balance > 1:
            path: list = [
                self.user.token1.address,
                WETHADDRESS,
                self.user.token0.address,
            ]
            min_recieved = self.get_amounts_out(
                self.user.token1.raw_balance, path)

            print(
                f"""
====================================================================|
Reversed Path:\n
Out: {self.user.token1.symbol} : ${self.user.token1.readable_balance}\n
In:  {self.user.token0.symbol} : ${CHAIN_TOOLS.to_readable_value(min_recieved,self.user.token0.decimals)}\n
- Potential Profit: ${CHAIN_TOOLS.to_readable_value(min_recieved,self.user.token0.decimals)-Decimal(self.user.token1.readable_balance + transaction_cost)}\n
====================================================================|\n
"""
            )

            if (
                CHAIN_TOOLS.to_readable_value(
                    min_recieved, self.user.token0.decimals)
                > self.user.token1.readable_balance + transaction_cost
            ):
                print("Arbitrage Opportunity Found!")

                if self.user.token1.approve(
                    self.__router_address, self.user.token1.readable_balance
                ):
                    self.execute_router_exact_tokens_for_tokens(
                        self.user.token1.raw_balance, path, min_recieved
                    )
                    return True
        else:
            print("No Arbitrage Opportunity Found")

            return False
