from decimal import Decimal 

from web3 import Web3
from eth_account import Account
from eth_typing import (  # // Link to docs: https://shorturl.at/cBJ28 // #
    ChecksumAddress,
    TypeStr,
)

from arbeth.src2.__settings import *
from arbeth.src2.__ChainTools import ChainTools

SETTINGS_BUFFER  = SettingsBuffer(network_index=0)._load_session_settings
W3: Web3 = Web3(Web3.HTTPProvider(SETTINGS_BUFFER.api)) #type: ingore
PRIVATE_KEY = Web3.to_checksum_address(SETTINGS_BUFFER.private_key)
PUBLIC_KEY = Web3.to_checksum_address(SETTINGS_BUFFER.public_key)
CHAIN_TOOLS = ChainTools(settings = SETTINGS_BUFFER,W3 = W3)

class User:

    _instance = None

    def __new__(cls,token0=None,token1=None):
        if cls._instance is None:
            cls._instance = super(User, cls).__new__(cls)
            cls._instance.initialize(token0, token1)
        return cls._instance
    
    def initialize(self,token0,token1):
        self.account:Account = Account.from_key(PRIVATE_KEY)
        self.address:ChecksumAddress = PUBLIC_KEY
        self.nonce = W3.eth.get_transaction_count(self.address)
        self.key = self.account.key #type: ignore
        self.token0 = token0
        self.token1 = token1


class ERC20Token:
    def __init__(self,address:str):
        self.address:ChecksumAddress = Web3.to_checksum_address(address)

        self.contract = W3.eth.contract(address=self.address,abi=SETTINGS_BUFFER.erc_20_abi)

        self.name: str = self.contract.functions.name().call()
        self.symbol: str = self.contract.functions.symbol().call()
        self.decimals: int = self.contract.functions.decimals().call()
        self.readableBalance: Decimal = (
            Decimal(self.contract.functions.balanceOf(PUBLIC_KEY).call())/ 10**self.decimals
        )
        self.rawBalance:int = self.contract.functions.balanceOf(PUBLIC_KEY) #type: ignore

    # -- Methods
    def getAllowance(self,spender: ChecksumAddress):
        return self.contract.functions.allowance(PUBLIC_KEY,spender).call()
    
    def approve(self, spender: ChecksumAddress, amount: Decimal):
        if self.getAllowance(spender) >= CHAIN_TOOLS.to_raw_value(
            amount, self.decimals
        ):
            return True

        else:
            transaction = CHAIN_TOOLS.transaction_dict #! Finish class method on chaintools

            builtTransaction = self.contract.functions.approve(
                spender, CHAIN_TOOLS.to_raw_value(amount, self.decimals)
            ).build_transaction(
                transaction  # type: ignore
            )

            signedTX = W3.eth.account.sign_transaction(builtTransaction, PRIVATE_KEY)
            if Web3.to_hex(
                W3.eth.send_raw_transaction(transaction=signedTX.rawTransaction)
            ):
                return True
            else:
                print("Error during approve contract call")
                return False
            

class V2Dex:
    def __init__(self,dex_name:str, router_address:str, factory_address:str, user: User):
        self.name =  dex_name
        self.user = user

        #addresses
        self.__oracle_address:ChecksumAddress = Web3.to_checksum_address(SETTINGS_BUFFER.oracle)
        self.__router_address:ChecksumAddress = Web3.to_checksum_address(router_address)
        self.__factory_address:ChecksumAddress = Web3.to_checksum_address(factory_address)

        #Contracts
        self.router_contract = W3.eth.contract(address = self.__router_address,abi = TypeStr(SETTINGS_BUFFER.sushi_rout_ABI))
        self.factory_contract = W3.eth.contract(address = self.__factory_address,abi=TypeStr(SETTINGS_BUFFER.uni_fact_ABI))
        self.oracle_contract = W3.eth.contract(address = self.__oracle_address,abi = TypeStr(SETTINGS_BUFFER.oracle_abi))

    def get_amounts_out(self,amount_in:int,path:list):
        return self.router_contract.functions.getAmountsOut(amount_in,path).call()
    
    def scan_for_arbitrage(self):
        pass

    def execute_router_exact_ETH_for_tokens(self):
        pass

    def execute_router_exact_tokens_for_tokens(self):
        pass

