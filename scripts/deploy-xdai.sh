#!/bin/bash
echo "-------------------------------------------"
echo "------------ Deploying to xDAI ------------"
echo "-------------------------------------------"
export WEB3_INFURA_PROJECT_ID=e22eadb98be944d18e48ab4bec7ecf3f
. ./venv/bin/activate
pip install -r requirements.txt

brownie networks add ethereum xdai chainid=100 host=https://xdai.poanetwork.dev
brownie run deploy-xdai --network xdai



