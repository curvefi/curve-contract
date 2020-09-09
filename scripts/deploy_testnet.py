# Testnet deployment script

import json
import time
from web3 import middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy as gas_strategy
from brownie import (
        web3, accounts,
        ERC20CRV, VotingEscrow, ERC20, ERC20LP, CurvePool,
        GaugeController, Minter, LiquidityGauge, PoolProxy, VestingEscrow, LiquidityGaugeReward, CurveRewards
        )


USE_STRATEGIES = False  # Needed for the ganache-cli tester which doesn't like middlewares
POA = True

# DEPLOYER = "0xFD3DeCC0cF498bb9f54786cb65800599De505706"
ARAGON_AGENT = "0x22D61abd46F14D40Ca9bF8eDD9445DCF29208589"

DISTRIBUTION_AMOUNT = 10 ** 6 * 10 ** 18
DISTRIBUTION_ADDRESSES = ["0x39415255619783A2E71fcF7d8f708A951d92e1b6", "0x6cd85bbb9147b86201d882ae1068c67286855211"]
VESTING_ADDRESSES = ['0x6637e8531d68917f5Ec31D6bA5fc80bDB34d9ef1']

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

CONFS = 1


def repeat(f, *args):
    """
    Repeat when geth is not broadcasting (unaccounted error)
    """
    while True:
        try:
            return f(*args)
        except KeyError:
            continue


def save_abi(contract, name):
    with open('%s.abi' % name, 'w') as f:
        json.dump(contract.abi, f)


def deploy_erc20s_and_pool(deployer):
    coin_a = repeat(ERC20.deploy, "Coin A", "USDA", 18, {'from': deployer, 'required_confs': CONFS})
    repeat(coin_a._mint_for_testing, 10 ** 9 * 10 ** 18, {'from': deployer, 'required_confs': CONFS})
    coin_b = repeat(ERC20.deploy, "Coin B", "USDB", 18, {'from': deployer, 'required_confs': CONFS})
    repeat(coin_b._mint_for_testing, 10 ** 9 * 10 ** 18, {'from': deployer, 'required_confs': CONFS})

    lp_token = repeat(ERC20LP.deploy, "Some pool", "cPool", 18, 0, {'from': deployer, 'required_confs': CONFS})
    save_abi(lp_token, 'lp_token')
    pool = repeat(CurvePool.deploy, [coin_a, coin_b], lp_token, 100, 4 * 10 ** 6, {'from': deployer, 'required_confs': CONFS})
    save_abi(pool, 'curve_pool')
    repeat(lp_token.set_minter, pool, {'from': deployer, 'required_confs': CONFS})

    registry = repeat(Registry.deploy, [ZERO_ADDRESS] * 4, {'from': deployer, 'required_confs': CONFS})
    save_abi(registry, 'registry')

    for account in DISTRIBUTION_ADDRESSES:
        repeat(coin_a.transfer, account, DISTRIBUTION_AMOUNT, {'from': deployer, 'required_confs': CONFS})
        repeat(coin_b.transfer, account, DISTRIBUTION_AMOUNT, {'from': deployer, 'required_confs': CONFS})

    repeat(pool.commit_transfer_ownership, ARAGON_AGENT, {'from': deployer, 'required_confs': CONFS})
    repeat(pool.apply_transfer_ownership, {'from': deployer, 'required_confs': CONFS})

    repeat(registry.commit_transfer_ownership, ARAGON_AGENT, {'from': deployer, 'required_confs': CONFS})
    repeat(registry.apply_transfer_ownership, {'from': deployer, 'required_confs': CONFS})

    return [lp_token, coin_a]


def main():
    if USE_STRATEGIES:
        web3.eth.setGasPriceStrategy(gas_strategy)
        web3.middleware_onion.add(middleware.time_based_cache_middleware)
        web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        web3.middleware_onion.add(middleware.simple_cache_middleware)
        if POA:
            web3.middleware_onion.inject(middleware.geth_poa_middleware, layer=0)

    deployer = accounts.at(DEPLOYER)


    # deploy pools and gauges

    coin_a = repeat(ERC20.deploy, "Coin A", "USDA", 18, {'from': deployer, 'required_confs': CONFS})
    repeat(coin_a._mint_for_testing, 10 ** 9 * 10 ** 18, {'from': deployer, 'required_confs': CONFS})
    coin_b = repeat(ERC20.deploy, "Coin B", "USDB", 18, {'from': deployer, 'required_confs': CONFS})
    repeat(coin_b._mint_for_testing, 10 ** 9 * 10 ** 18, {'from': deployer, 'required_confs': CONFS})

    lp_token = repeat(ERC20LP.deploy, "Some pool", "cPool", 18, 0, {'from': deployer, 'required_confs': CONFS})
    save_abi(lp_token, 'lp_token')
    pool = repeat(CurvePool.deploy, [coin_a, coin_b], lp_token, 100, 4 * 10 ** 6, {'from': deployer, 'required_confs': CONFS})
    save_abi(pool, 'curve_pool')
    repeat(lp_token.set_minter, pool, {'from': deployer, 'required_confs': CONFS})

    repeat(coin_a.transfer, '0x6cd85bbb9147b86201d882ae1068c67286855211', DISTRIBUTION_AMOUNT, {'from': deployer, 'required_confs': CONFS})
    repeat(coin_b.transfer, '0x6cd85bbb9147b86201d882ae1068c67286855211', DISTRIBUTION_AMOUNT, {'from': deployer, 'required_confs': CONFS})

    contract = repeat(CurveRewards.deploy, lp_token, coin_a, {'from': accounts[0], 'required_confs': CONFS})
    repeat(contract.setRewardDistribution, accounts[0], {'from': accounts[0], 'required_confs': CONFS})
    repeat(coin_a.transfer, contract, 100e18, {'from': accounts[0], 'required_confs': CONFS})

    liquidity_gauge_rewards = repeat(LiquidityGaugeReward.deploy, lp_token, '0xbE45e0E4a72aEbF9D08F93E64701964d2CC4cF96', contract, coin_a, {'from': deployer, 'required_confs': CONFS})


    coins = deploy_erc20s_and_pool(deployer)

    lp_token = coins[0]
    coin_a = coins[1]

    token = repeat(ERC20CRV.deploy, "Curve DAO Token", "CRV", 18, {'from': deployer, 'required_confs': CONFS})
    save_abi(token, 'token_crv')

    escrow = repeat(VotingEscrow.deploy, token, "Vote-escrowed CRV", "veCRV", "veCRV_0.99", {'from': deployer, 'required_confs': CONFS})
    save_abi(escrow, 'voting_escrow')

    repeat(escrow.changeController, ARAGON_AGENT, {'from': deployer, 'required_confs': CONFS})

    for account in DISTRIBUTION_ADDRESSES:
        repeat(token.transfer, account, DISTRIBUTION_AMOUNT, {'from': deployer, 'required_confs': CONFS})

    gauge_controller = repeat(GaugeController.deploy, token, escrow, {'from': deployer, 'required_confs': CONFS})
    save_abi(gauge_controller, 'gauge_controller')

    minter = repeat(Minter.deploy, token, gauge_controller, {'from': deployer, 'required_confs': CONFS})
    save_abi(minter, 'minter')

    liquidity_gauge = repeat(LiquidityGauge.deploy, lp_token, minter, {'from': deployer, 'required_confs': CONFS})
    save_abi(liquidity_gauge, 'liquidity_gauge')

    contract = repeat(CurveRewards.deploy, lp_token, coin_a, {'from': accounts[0], 'required_confs': CONFS})
    repeat(contract.setRewardDistribution, accounts[0], {'from': accounts[0], 'required_confs': CONFS})
    repeat(coin_a.transfer, contract, 100e18, {'from': accounts[0], 'required_confs': CONFS})

    liquidity_gauge_rewards = repeat(LiquidityGaugeReward.deploy, lp_token, minter, contract, coin_a, {'from': deployer, 'required_confs': CONFS})

    repeat(token.set_minter, minter, {'from': deployer, 'required_confs': CONFS})
    repeat(gauge_controller.add_type, b'Liquidity', {'from': deployer, 'required_confs': CONFS})
    repeat(gauge_controller.change_type_weight, 0, 10 ** 18, {'from': deployer, 'required_confs': CONFS})
    repeat(gauge_controller.add_gauge, liquidity_gauge, 0, 10 ** 18, {'from': deployer, 'required_confs': CONFS})

    repeat(gauge_controller.add_type, b'LiquidityRewards', {'from': deployer, 'required_confs': CONFS})
    repeat(gauge_controller.change_type_weight, 1, 10 ** 18, {'from': deployer, 'required_confs': CONFS})
    repeat(gauge_controller.add_gauge, liquidity_gauge_rewards, 1, 10 ** 18, {'from': deployer, 'required_confs': CONFS})

    repeat(gauge_controller.commit_transfer_ownership, ARAGON_AGENT, {'from': deployer, 'required_confs': CONFS})
    repeat(gauge_controller.apply_transfer_ownership, {'from': deployer, 'required_confs': CONFS})
    repeat(escrow.commit_transfer_ownership, ARAGON_AGENT, {'from': deployer, 'required_confs': CONFS})
    repeat(escrow.apply_transfer_ownership, {'from': deployer, 'required_confs': CONFS})

    repeat(PoolProxy.deploy, {'from': deployer, 'required_confs': CONFS})

    vesting = repeat(VestingEscrow.deploy, token, time.time() + 300, '1628364267', False, {'from': deployer, 'required_confs': CONFS})
    save_abi(vesting, 'vesting')

    repeat(token.approve, vesting, 1000e18, {'from': deployer, 'required_confs': CONFS})
    repeat(vesting.fund, VESTING_ADDRESSES + ['0x0000000000000000000000000000000000000000']*9, [1000e18] + [0]*9, {'from': deployer, 'required_confs': CONFS})


