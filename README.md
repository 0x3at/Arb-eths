# ArbEths

ArbEths is a primitive arbitrage interface containing classes for easy stablecoin arbitrage. The following are requirements before instantiation. 

1. Creat and Activate a python venv
```bash
$ python -m venv .env
$ source .env/bin/activate
```
```Windows
.env\Scripts\Activate
```

2. Fill in the env.txt and convert to .env when done 
``` .env
Required Fields
INFURA_ETH_API = 
ALCHEMY_GOERLI_API =  
ALCHEMY_ETH_API = 
ARBITRUM_API = 
AVAX_API = 

PRIVATE_KEY = 
PULIC_KEY =
```

3. Instantiate the Token Pair by creating a new `ERC20Token`
``` Python
usdt = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
usdce = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"

USDT = ERC20Token(usdt)
USDCE = ERC20Token(usdce)
```

4. Create a User Object(Singleton)
``` Python
user = User(USDT, USDCE)
```

5. Create an Instance of the specified DEX 
``` Python
sushiswap = UNIV2Clone(
  dexName: str ="Sushiswap V2",
  routerAddress: str = routerNETWORK.UNIv2router, 
  factoryAddress: str = NETWORK.UNIv2factory,
  user: User = user
 )
```

6. Run the Main loop, passing your objects as arguments 
``` Python
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
```


 
