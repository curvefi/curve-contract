# Testnet deployment script

import json
from web3 import middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy as gas_strategy
from brownie import (
        web3, accounts,
        ERC20CRV, VotingEscrow, ERC20, ERC20LP, CurvePool, Registry,
        GaugeController, Minter, LiquidityGauge, LiquidityGaugeReward, PoolProxy, CurveRewards
        )

SEED = 'explain tackle mirror kit van hammer degree position ginger unfair soup bonus'
confs = 1
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ARAGON_AGENT = "0xa01556dB443292BD3754C1CCd0B9ecFE8CE9E356"
DISTRIBUTION_AMOUNT = 10 ** 6 * 10 ** 18
DISTRIBUTION_ADDRESSES = ["0x39415255619783A2E71fcF7d8f708A951d92e1b6", "0x6cd85bbb9147b86201d882ae1068c67286855211"]

def main():
accounts.from_mnemonic(SEED)
admin = accounts[0]


token = ERC20CRV.deploy("Curve DAO Token", "CRV", 18, {'from': admin, 'required_confs': confs})
voting_escrow = VotingEscrow.deploy(
    token, "Vote-escrowed CRV", "veCRV", "veCRV_1.0.0", {'from': admin, 'required_confs': confs}
)


coin_a = ERC20.deploy("Coin A", "USDA", 18, {'from': admin, 'required_confs': confs})
coin_b = ERC20.deploy("Coin B", "USDB", 18, {'from': admin, 'required_confs': confs})
coin_a._mint_for_testing(10 ** 9 * 10 ** 18, {'from': admin, 'required_confs': confs})
coin_b._mint_for_testing(10 ** 9 * 10 ** 18, {'from': admin, 'required_confs': confs})

lp_token = ERC20LP.deploy("Some pool", "cPool", 18, 0, {'from': admin, 'required_confs': confs})
pool = CurvePool.deploy([coin_a, coin_b], lp_token, 100, 4 * 10 ** 6, {'from': admin, 'required_confs': confs})
lp_token.set_minter(pool, {'from': admin, 'required_confs': confs})

coin_a.approve(pool, "1000000000000000000000", {'from': admin})
coin_b.approve(pool, "1000000000000000000000", {'from': admin})
pool.add_liquidity(["100000000000000", "200000000000000"], 0, {'from': admin})

contract = CurveRewards.deploy(lp_token, coin_a, {'from': accounts[1], 'required_confs': confs})
contract.setRewardDistribution(accounts[0], {'from': accounts[1], 'required_confs': confs})
registry = Registry.deploy([ZERO_ADDRESS] * 4, {'from': admin, 'required_confs': confs})

coin_a.transfer(contract, 100e18, {'from': accounts[1], 'required_confs': confs})

liquidity_gauge_rewards = LiquidityGaugeReward.deploy(lp_token, '0xbE45e0E4a72aEbF9D08F93E64701964d2CC4cF96', contract, coin_a, {'from': admin, 'required_confs': confs})

for account in DISTRIBUTION_ADDRESSES:
    coin_a.transfer(account, DISTRIBUTION_AMOUNT, {'from': admin, 'required_confs': confs})
    coin_b.transfer(account, DISTRIBUTION_AMOUNT, {'from': admin, 'required_confs': confs})

pool.commit_transfer_ownership(ARAGON_AGENT, {'from': admin, 'required_confs': confs})
pool.apply_transfer_ownership({'from': admin, 'required_confs': confs})
registry.commit_transfer_ownership(ARAGON_AGENT, {'from': admin, 'required_confs': confs})
registry.apply_transfer_ownership({'from': admin, 'required_confs': confs})

gauge_controller = GaugeController.deploy(token, voting_escrow, {'from': admin, 'required_confs': confs})
minter = Minter.deploy(token, gauge_controller, {'from': admin, 'required_confs': confs})
liquidity_gauge = LiquidityGauge.deploy(lp_token, minter, {'from': admin, 'required_confs': confs})

token.set_minter(minter, {'from': admin, 'required_confs': confs})
gauge_controller.add_type(b'Liquidity', {'from': admin, 'required_confs': confs})
gauge_controller.change_type_weight(0, 10 ** 18, {'from': admin, 'required_confs': confs})
gauge_controller.add_gauge(liquidity_gauge, 0, 10 ** 18, {'from': admin, 'required_confs': confs})

gauge_controller.commit_transfer_ownership(ARAGON_AGENT, {'from': admin, 'required_confs': confs})
gauge_controller.apply_transfer_ownership({'from': admin, 'required_confs': confs})
voting_escrow.commit_transfer_ownership(ARAGON_AGENT, {'from': admin, 'required_confs': confs})
voting_escrow.apply_transfer_ownership({'from': admin, 'required_confs': confs})

PoolProxy.deploy({'from': admin, 'required_confs': confs})