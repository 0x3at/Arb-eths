from _settings import *


class ConfigurationInjector:
    # ? Need to update network initializer
    # ? Add class attribute that is a list of networks
    # ? Change `network_name` to `network_index`
    # ? User passes int argument of the index
    # // Example:
    # ? atr : list = [eth,arbitrum,avax] | arg : int = list index
    _instance = None

    def __new__(cls, network_name: str, test_run: bool = False):
        if cls._instance is None:
            cls._instance = super(ConfigurationInjector, cls).__new__(cls)
            cls._instance.config = cls._load_network_config(  # type:ignore
                network_name, test_run
            )
        return cls._instance

    @staticmethod
    def _load_network_config(network_name, test_run):
        if network_name.lower() == "eth" or network_name.lower() == "ethmainnet":
            return EthMainNet(test_run=test_run)
        elif (
            network_name.lower() == "arbitrum"
            or network_name.lower() == "arbitrummainnet"
        ):
            return ArbitrumMainNet(test_run=test_run)
        elif network_name.lower() == "avax" or network_name.lower() == "avaxmainnet":
            return AvaxMainNet(test_run=test_run)
        else:
            print(
                "Invalid network name.\nPlease choose from:\n[eth],\n[arbitrum},\n[avax],\n[goerli]."
            )
            exit(1)
