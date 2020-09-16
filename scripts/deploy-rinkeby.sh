#!/bin/bash
echo "--------------------------------------------"
echo "----------- Deploying to Rinkeby -----------"
echo "--------------------------------------------"
export WEB3_INFURA_PROJECT_ID=e22eadb98be944d18e48ab4bec7ecf3f
. ./venv/bin/activate
pip install -r requirements.txt

brownie run deploy-rinkeby --network rinkeby