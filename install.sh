#!/bin/bash

virtualenv -p python3 .venv
source .venv/bin/activate
pip3 install -r requirements.txt

SOLC_VER="0.5.11"
SOL_BIN_PATH="$(dirname `which python3`)/solc"

echo "Downloading solidity compiler binary to: ${SOL_BIN_PATH}"
wget "https://github.com/ethereum/solidity/releases/download/v${SOLC_VER}/solc-static-linux" -O ${SOL_BIN_PATH}
echo "Setting executable permission on ${SOL_BIN_PATH}"
chmod +x ${SOL_BIN_PATH}
echo "Successfully Installed solc ${SOLC_VER}"
