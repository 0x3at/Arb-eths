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

from _configInjector import ConfigurationInjector
from _chainmanagerC import ChainManager


# -- List of configred networks
networks = ["eth", "arbitrum", "avax"]


# --  Retrieve Network Configurations
NETWORK = ConfigurationInjector(networks[1]).config  # type: ignore #

PRIVATEKEY = NETWORK.privateKey
APISTRING = NETWORK.api
WETHADDRESS = Web3.to_checksum_address(NETWORK.weth)
W3: Web3 = Web3(Web3.HTTPProvider(APISTRING))
PUBLICKEY = W3.to_checksum_address(NETWORK.publicKey)


# -- On Chain Utlity Class (Estimation, Building, & Conversion)
chain_helper = ChainManager(
    WETHADDRESS,
    W3.to_checksum_address(NETWORK.oracle),
    NETWORK.erc_20_ABI,
    NETWORK.oracle_ABI,
    W3,
    PUBLICKEY,
)


class User:
    _instance = None  # Singleton Implementation

    def __new__(cls, token0=None, token1=None):
        if cls._instance is None:
            cls._instance = super(User, cls).__new__(cls)
            cls._instance.initialize(token0, token1)
        return cls._instance

    def initialize(self, token0=None, token1=None):
        # -- Constants
        self.account = Account.from_key(PRIVATEKEY)
        self.address = self.account.address
        self.nonce = W3.eth.get_transaction_count(self.address)
        self.key = self.account.key
        self.token0 = token0
        self.token1 = token1


class ERC20Token:
    def __init__(self, address: str):
        # -- Constants
        self.address: ChecksumAddress = Web3.to_checksum_address(address)

        # Callable Contracts
        self.contract = W3.eth.contract(address=self.address, abi=NETWORK.erc_20_ABI)

        # -- Token Data
        self.name: str = self.contract.functions.name().call()
        self.symbol: str = self.contract.functions.symbol().call()
        self.decimals: int = self.contract.functions.decimals().call()
        self.readableBalance: Decimal = (
            Decimal(self.contract.functions.balanceOf(PUBLICKEY).call())
            / 10**self.decimals
        )
        self.rawBalance: int = self.contract.functions.balanceOf(PUBLICKEY).call()

    # -- Class Methods
    def getAllowance(self, spender: ChecksumAddress):
        return self.contract.functions.allowance(PUBLICKEY, spender).call()

    def approve(self, spender: ChecksumAddress, amount: Decimal):
        if self.getAllowance(spender) >= chain_helper.to_raw_value(
            amount, self.decimals
        ):
            return True

        else:
            transaction = chain_helper.retrieve_transaction_dict()

            builtTransaction = self.contract.functions.approve(
                spender, chain_helper.to_raw_value(amount, self.decimals)
            ).build_transaction(
                transaction  # type: ignore
            )

            signedTX = W3.eth.account.sign_transaction(builtTransaction, PRIVATEKEY)
            if Web3.to_hex(
                W3.eth.send_raw_transaction(transaction=signedTX.rawTransaction)
            ):
                return True
            else:
                print("Error during approve contract call")
                return False


class UNIV2Clone:
    def __init__(self, dexName, routerAddress: str, factoryAddress: str, user: User):
        # -- Constants
        self.name = dexName
        self.user = user

        # -- Addresses
        self.oracleAddress: ChecksumAddress = W3.to_checksum_address(NETWORK.oracle)
        self.routerAddress: ChecksumAddress = W3.to_checksum_address(routerAddress)
        self.factoryAddress: ChecksumAddress = W3.to_checksum_address(factoryAddress)

        # -- Callable Contracts
        self.routerContract = W3.eth.contract(
            address=self.routerAddress, abi=NETWORK.uni_rout_ABI
        )
        self.factoryContract = W3.eth.contract(
            address=self.factoryAddress, abi=NETWORK.uni_fact_ABI
        )
        self.oracleContract = W3.eth.contract(
            address=self.oracleAddress, abi=NETWORK.oracle_ABI
        )

    # -- Class Methods
    # TODO: Convert amountIn to raw value before calling function
    def getAmountsOutQuote(self, amountIn: int, path: list):
        return self.routerContract.functions.getAmountsOut(amountIn, path).call()

    def calculate_arbitrage_opp(self):
        pass

    def executeRouterExactETHforTokensSwap(self):
        pass

    def executeRouterExactTokensforTokensSwap(self):
        pass


# // usdt = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
# // dai = "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1"

# // USDT = ERC20Token(usdt)
# // DAI = ERC20Token(dai)

# // user = User(USDT, DAI)
# // print(user.token0)
# // print(user.token1)
