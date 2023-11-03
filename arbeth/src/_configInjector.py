from _settings import *


class ConfigurationInjector:
    _instance = None

    def __new__(cls, network_name):
        if cls._instance is None:
            cls._instance = super(ConfigurationInjector, cls).__new__(cls)
            cls._instance.config = cls._load_network_config(network_name)  # type:ignore
        return cls._instance

    @staticmethod
    def _load_network_config(network_name):
        if network_name.lower() == "eth" or network_name.lower() == "ethmainnet":
            return EthMainNet()
        elif (
            network_name.lower() == "arbitrum"
            or network_name.lower() == "arbitrummainnet"
        ):
            return ArbitrumMainNet()
        elif network_name.lower() == "avax" or network_name.lower() == "avaxmainnet":
            return AvaxMainNet()
        # elif network_name.lower() == "goerli" or network_name.lower() == "ethgoerli":
        #     return ETHGoerli()
        else:
            print(
                "Invalid network name.\nPlease choose from:\n[eth],\n[arbitrum},\n[avax],\n[goerli]."
            )
            exit(1)
