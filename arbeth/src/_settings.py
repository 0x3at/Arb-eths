from dotenv import load_dotenv, find_dotenv
from os import environ
import json

load_dotenv(find_dotenv())


# Injects Constants into Network Classes
class NetworkConstants:
    def __init__(self):
        self.privateKey = environ.get("PRIVATE_KEY")
        self.publicKey = environ.get("PUBLIC_KEY")

        # Initialize ABIs in the base class
        with open(environ.get("PATH_TO_ERC_ABI")) as erc20ABI:  # type: ignore
            self.erc_20_ABI = json.load(erc20ABI)
        with open(environ.get("PATH_TO_UNI_LP_ABI")) as uniLPABI:  # type: ignore
            self.uni_lp_ABI = json.load(uniLPABI)
        with open(environ.get("PATH_TO_UNI_FACT_ABI")) as uniFactABI:  # type: ignore
            self.uni_fact_ABI = json.load(uniFactABI)
        with open(environ.get("PATH_TO_SUSHI_ROUTER_ABI")) as sushiRoutAbi:  # type: ignore
            self.sushi_rout_ABI = json.load(sushiRoutAbi)
        with open(environ.get("PATH_TO_ORACLE_ABI")) as oracleABI:  # type: ignore
            self.oracle_ABI = json.load(oracleABI)


# Eth Goerli TestNet
class EthGoerli(NetworkConstants):
    def __init__(self) -> None:
        super().__init__()  # Call Inherited Constructor

        # -- Testnet Constants
        self.name = "Ethereum Goerli Network"
        self.api = environ.get("ALCHEMY_GOERLI_API")
        self.weth = "0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6"
        self.UNIv2router = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
        self.UNIv2factory = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"


# Eth Mainnet
class EthMainNet(NetworkConstants):
    def __init__(self, test_run) -> None:
        # -- Session Configurations
        super().__init__()  # Call Inherited Constructor
        self.testRun = test_run

        # --  Mainnet Constants
        if not test_run:
            self.name = "Ethereum"
            self.api = environ.get("ALCHEMY_ETH_API")
            self.oracle = "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419"
            self.weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            self.UNIv2router = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
            self.UNIv2factory = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
            self.PancakeRouter = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
            self.PancakeFactory = "0x1097053Fd2ea711dad45caCcc45EfF7548fCB362"
            self.FraxRouter = "0xC14d550632db8592D1243Edc8B95b0Ad06703867"
            self.FraxFactory = "0x43eC799eAdd63848443E2347C49f5f52e8Fe0F6f"

        # -- Testnet Constants
        if test_run:
            self.testNet = EthGoerli()
            self.name = self.testNet.name
            self.api = self.testNet.api
            # self.oracle = self.testNet.oracle #? Add Oracle to TestNet Class
            self.weth = self.testNet.weth
            self.UNIv2router = self.testNet.UNIv2router
            self.UNIv2factory = self.testNet.UNIv2factory


# Arbitrum Mainnet
class ArbitrumMainNet(NetworkConstants):
    def __init__(self, test_run) -> None:
        super().__init__()  # Call Inherited Constructor
        self.testRun = test_run

        # -- Mainnet Constants
        self.name = "Arbitrum One"
        self.api = environ.get("ARBITRUM_API")
        self.oracle = "0x639fe6ab55c921f74e7fac1ee960c0b6293ba612"
        self.weth = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
        self.UNIv2router = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
        self.UNIv2factory = "0xc35DADB65012eC5796536bD9864eD8773aBc74C4"
        self.PancakeRouter = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
        self.PancakeFactory = "0x02a84c1b3BBD7401a5f7fa98a384EBC70bB5749E"
        self.FraxRouter = "0xCAAaB0A72f781B92bA63Af27477aA46aB8F653E7"
        self.FraxFactory = "0x8374A74A728f06bEa6B7259C68AA7BBB732bfeaD"


# Avax Mainnet
class AvaxMainNet(NetworkConstants):
    def __init__(self, test_run) -> None:
        super().__init__()  # Call Inherited Constructor
        self.testRun = test_run

        # -- Mainnet Constants
        self.name = "Avax Mainnet"
        self.api = environ.get("AVAX_API")
        self.oracle = "0x976b3d034e162d8bd72d6b9c989d545b839003b0"
        self.weth = "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7"
        self.UNIv2router = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
        self.UNIv2factory = "0xc35DADB65012eC5796536bD9864eD8773aBc74C4"
        self.FraxRouter = "0x5977b16AA9aBC4D1281058C73B789C65Bf9ab3d3"
        self.FraxFactory = "0xf77ca9B635898980fb219b4F4605C50e4ba58afF"
