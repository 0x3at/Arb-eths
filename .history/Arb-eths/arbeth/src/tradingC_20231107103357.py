from dotenv import load_dotenv
from os import getenv
from decimal import Decimal
import time

from web3 import Web3, exceptions  # // Link to docs: https://shorturl.at/agMQX // #
from eth_account import Account  # // Link to docs: https://shorturl.at/sHW39 // #
from eth_typing import (  # // Link to docs: https://shorturl.at/cBJ28 // #
    ChecksumAddress,
    TypeStr,
)

from _configInjector import ConfigurationInjector
from _chainmanagerC import ChainManager


# -- List of configured networks
networks = ["eth", "arbitrum", "avax"]


# --  Retrieve Network Configurations
NETWORK = ConfigurationInjector(networks[1]).config  # type: ignore #

PRIVATEKEY = NETWORK.privateKey
APISTRING = NETWORK.api
WETHADDRESS = Web3.to_checksum_address(NETWORK.weth)

W3: Web3 = Web3(Web3.HTTPProvider(APISTRING))
PUBLICKEY = W3.to_checksum_address(NETWORK.publicKey)

try:
    W3.is_connected()
    print(f"Connected to {NETWORK.name} : {W3.is_connected()}")
except:
    print("Error: Unable to connect to network")
    exit(1)

# -- On Chain Utlity Class (Estimation, Building, & Conversion)
chain_helper = ChainManager(
    WETHADDRESS,
    W3.to_checksum_address(NETWORK.oracle),
    NETWORK.erc_20_ABI,
    NETWORK.oracle_ABI,
    W3,
    PUBLICKEY,
)


class ERC20Token:
    def __init__(self, address: str):
        # -- Constants
        self.address: ChecksumAddress = Web3.to_checksum_address(address)

        # Callable Contracts
        self.contract = W3.eth.contract(address=self.address, abi=NETWORK.erc_20_ABI)

        # -- Token Data
        try:
            self.name: str = self.contract.functions.name().call()
            self.symbol: str = self.contract.functions.symbol().call()
            self.decimals: int = self.contract.functions.decimals().call()
            self.readableBalance: Decimal = (
                Decimal(self.contract.functions.balanceOf(PUBLICKEY).call())
                / 10**self.decimals
            )
            self.rawBalance: int = self.contract.functions.balanceOf(PUBLICKEY).call()
        except (BadFunctionCallException, ContractLogicError) as e:
    # Handle smart contract errors
    print(f"Smart contract error: {e}")
except ConnectionError as e:
    # Handle connection errors
    print(f"Connection error: {e}")
except TimeExhausted as e:
    # Handle timeout errors
    print(f"Timeout error: {e}")
except ValueError as e:
    # Handle incorrect value formats
    print(f"Value error: {e}")
except Exception as e:
    # Handle any other exceptions
    print(f"An unexpected error occurred: {e}")


    # -- Class Methods
    def getAllowance(self, spender: ChecksumAddress):
        return self.contract.functions.allowance(PUBLICKEY, spender).call()

    def approve(self, spender: ChecksumAddress, amount: Decimal):
        if self.getAllowance(spender) >= chain_helper.to_raw_value(
            amount, self.decimals
        ):
            return True

        else:
            print("Approving Spend Limit...\n")
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
                print("Spend Limit Approved\n")
                return True
            else:
                print("Error during approve contract call\n")
                return False


# ! Needs to be isolated in its own file and imported through the injector
class User:
    _instance = None  # Singleton Implementation

    def __new__(cls, token0: ERC20Token, token1: ERC20Token):
        if cls._instance is None:
            cls._instance = super(User, cls).__new__(cls)
            cls._instance.initialize(token0, token1)
        return cls._instance

    def initialize(self, token0, token1):
        # -- Constants
        self.account = Account.from_key(PRIVATEKEY)
        self.address = self.account.address
        self.nonce = W3.eth.get_transaction_count(self.address)
        self.key = self.account.key
        self.token0 = token0
        self.token1 = token1


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
            address=self.routerAddress, abi=NETWORK.sushi_rout_ABI
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

    def executeRouterExactETHforTokensSwap(self):
        pass

    def executeRouterExactTokensforTokensSwap(
        self, amountIn: int, path: list, amountOutMin: int
    ):
        transaction = chain_helper.transaction_dict

        built_transaction = self.routerContract.functions.swapExactTokensForTokens(
            amountIn, amountOutMin, path, PUBLICKEY, int(time.time() + 60)
        ).build_transaction(
            transaction  # type: ignore
        )
        signedTX = W3.eth.account.sign_transaction(built_transaction, PRIVATEKEY)

        tx_hash = W3.eth.send_raw_transaction(transaction=signedTX.rawTransaction)
        try:
            tx_receipt = W3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            print("Transaction Successful\n")
            print(tx_receipt)
            return True
        except exceptions.TimeExhausted:
            print("Transaction Timed Out")
            return False

    def calculate_and_execute_arbitrage_opp(self):
        transaction_cost = chain_helper.get_gas_price_in_USD(None) - Decimal(0.1)

        print(f"Estimated TX Cost: ${transaction_cost}\n")

        path: list = [self.user.token0.address, WETHADDRESS, self.user.token1.address]
        min_recieved = self.routerContract.functions.getAmountsOut(
            int(self.user.token0.rawBalance), path
        ).call()[2]

        print(
            f"""
Starting Path:\n
Out: {self.user.token0.symbol} : {self.user.token0.readableBalance}\n
In:  {self.user.token1.symbol} : {chain_helper.to_readable_value(min_recieved,self.user.token1.decimals)}\n
- Potential Profit: {chain_helper.to_readable_value(min_recieved,self.user.token1.decimals)-Decimal(self.user.token0.readableBalance + transaction_cost)}
"""
        )

        if self.user.token0.readableBalance > 1:
            if (
                chain_helper.to_readable_value(min_recieved, self.user.token1.decimals)
                > self.user.token0.readableBalance + transaction_cost
            ):
                print("Arbitrage Opportunity Found!")

                if self.user.token0.approve(
                    self.routerAddress, self.user.token0.readableBalance
                ):
                    self.executeRouterExactTokensforTokensSwap(
                        self.user.token0.rawBalance, path, min_recieved
                    )
                    return True

        if self.user.token1.readableBalance > 1:
            path: list = [
                self.user.token1.address,
                WETHADDRESS,
                self.user.token0.address,
            ]
            min_recieved = self.routerContract.functions.getAmountsOut(
                int(self.user.token1.rawBalance), path
            ).call()[2]

            print(
                f"""
Reversed Path:\n
Out: {self.user.token1.symbol} : {self.user.token1.readableBalance}\n
In:  {self.user.token0.symbol} : {chain_helper.to_readable_value(min_recieved,self.user.token0.decimals)}\n
- Potential Profit: {chain_helper.to_readable_value(min_recieved,self.user.token0.decimals)-Decimal(self.user.token1.readableBalance + transaction_cost)}
"""
            )

            if (
                chain_helper.to_readable_value(min_recieved, self.user.token0.decimals)
                > self.user.token1.readableBalance + transaction_cost
            ):
                print("Arbitrage Opportunity Found!")

                if self.user.token1.approve(
                    self.routerAddress, self.user.token1.readableBalance
                ):
                    self.executeRouterExactTokensforTokensSwap(
                        self.user.token1.rawBalance, path, min_recieved
                    )
                    return True
        else:
            print("No Arbitrage Opportunity Found")

            return False

    def test_get_amounts_out(self):
        path: list = [self.user.token0.address, WETHADDRESS, self.user.token1.address]
        min_recieved = self.routerContract.functions.getAmountsOut(
            int(self.user.token0.rawBalance), path
        ).call()[2]
        return min_recieved


usdt = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
usdce = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"

USDT = ERC20Token(usdt)
USDCE = ERC20Token(usdce)
user = User(USDT, USDCE)

sushiswap = UNIV2Clone("Sushiswap V2", NETWORK.UNIv2router, NETWORK.UNIv2factory, user)

SCANNING = True
while SCANNING:
    try:
        if sushiswap.calculate_and_execute_arbitrage_opp():
            print("Swapping Pair...\n")
        else:
            time.sleep(3)
            print("Scanning...\n")

    except Exception as e:
        print(e)
        SCANNING = False
