brownie networks add Zetachain athens host="https://zetachain-athens-evm.blockpi.network/v1/rpc/public" chainid=7001

brownie networks modify athens host=https://zetachain-testnet-evm.itrocket.net

pip3 install urllib3==1.26.6
/Library/Developer/CommandLineTools/usr/bin/python3 -m pip install --upgrade pip

brownie run deploy --network athens

working versions:
pip: pip 24.0 from /Users/andresaiello/Library/Python/3.9/lib/python/site-packages/pip (python 3.9)
brownie: Brownie v1.14.5 - Python development framework for Ethereum