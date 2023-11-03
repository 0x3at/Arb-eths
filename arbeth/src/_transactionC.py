from dataclasses import dataclass


@dataclass
class TransactionC:
    chainId: int
    nonce: int
    gas: int
    maxFeePerGas: int
    maxPriorityFeePerGas: int
