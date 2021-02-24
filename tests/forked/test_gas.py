import itertools

import pytest
from brownie import ETH_ADDRESS


@pytest.fixture(scope="module", autouse=True)
def setup(mint_alice, approve_alice, mint_bob, approve_bob, set_fees):
    set_fees(4000000, 5000000000, include_meta=True)


def test_swap_gas(
    chain,
    alice,
    bob,
    swap,
    n_coins,
    wrapped_decimals,
    underlying_decimals,
    wrapped_coins,
    underlying_coins,
    initial_amounts,
):

    # add liquidity balanced
    amounts = [i // 2 for i in initial_amounts]
    value = amounts[0] if ETH_ADDRESS in wrapped_coins else 0
    swap.add_liquidity(amounts, 0, {"from": alice, "value": value})
    chain.sleep(3600)

    # add liquidity imbalanced
    for idx in range(n_coins):
        amounts = [i // 10 for i in initial_amounts]
        amounts[idx] = 0
        value = 0
        if ETH_ADDRESS in wrapped_coins:
            value = amounts[0]
        swap.add_liquidity(amounts, 0, {"from": alice, "value": value})
        chain.sleep(3600)

    # perform swaps between each coin
    for send, recv in itertools.permutations(range(n_coins), 2):
        amount = 10 ** wrapped_decimals[send]

        # retain a balance of the sent coin and start with 0 balance of receiving coin
        # this is the least gas-efficient method :)
        if wrapped_coins[send] != ETH_ADDRESS:
            wrapped_coins[send]._mint_for_testing(bob, amount + 1, {"from": bob})
        if wrapped_coins[recv] != ETH_ADDRESS:
            recv_balance = wrapped_coins[recv].balanceOf(bob)
            if recv_balance > 0:
                wrapped_coins[recv].transfer(alice, recv_balance, {"from": bob})

        value = 0 if wrapped_coins[send] != ETH_ADDRESS else amount
        swap.exchange(send, recv, amount, 0, {"from": bob, "value": value})
        chain.sleep(3600)

    # perform swaps between each underlying coin
    if hasattr(swap, "exchange_underlying"):
        for send, recv in itertools.permutations(range(n_coins), 2):
            amount = 10 ** underlying_decimals[send]

            underlying_coins[send]._mint_for_testing(bob, amount + 1, {"from": bob})
            recv_balance = underlying_coins[recv].balanceOf(bob)
            if recv_balance > 0:
                underlying_coins[recv].transfer(alice, recv_balance, {"from": bob})

            swap.exchange_underlying(send, recv, amount, 0, {"from": bob})
            chain.sleep(3600)

    # remove liquidity balanced
    swap.remove_liquidity(10 ** 18, [0] * n_coins, {"from": alice})
    chain.sleep(3600)

    amounts = [10 ** wrapped_decimals[i] for i in range(n_coins)]
    swap.remove_liquidity_imbalance(amounts, 2 ** 256 - 1, {"from": alice})
    chain.sleep(3600)

    # remove liquidity imbalanced
    for idx in range(n_coins):
        amounts = [10 ** wrapped_decimals[i] for i in range(n_coins)]
        amounts[idx] = 0
        swap.remove_liquidity_imbalance(amounts, 2 ** 256 - 1, {"from": alice})
        chain.sleep(3600)

    if hasattr(swap, "remove_liquidity_one_coin"):
        for idx in range(n_coins):
            swap.remove_liquidity_one_coin(10 ** wrapped_decimals[idx], idx, 0, {"from": alice})
            chain.sleep(3600)


@pytest.mark.zap
def test_zap_gas(
    chain, alice, zap, pool_token, underlying_decimals, initial_amounts_underlying, approve_zap,
):
    n_coins = len(initial_amounts_underlying)

    # add liquidity balanced
    zap.add_liquidity([i // 2 for i in initial_amounts_underlying], 0, {"from": alice})
    chain.sleep(3600)

    # add liquidity imbalanced
    for idx in range(n_coins):
        amounts = [i // 10 for i in initial_amounts_underlying]
        amounts[idx] = 0
        zap.add_liquidity(amounts, 0, {"from": alice})
        chain.sleep(3600)

    # remove liquidity balanced
    zap.remove_liquidity(10 ** 18, [0] * n_coins, {"from": alice})
    chain.sleep(3600)

    amounts = [10 ** underlying_decimals[i] for i in range(n_coins)]
    zap.remove_liquidity_imbalance(amounts, pool_token.balanceOf(alice), {"from": alice})
    chain.sleep(3600)

    # remove liquidity imbalanced
    for idx in range(n_coins):
        amounts = [10 ** underlying_decimals[i] for i in range(n_coins)]
        amounts[idx] = 0
        zap.remove_liquidity_imbalance(amounts, pool_token.balanceOf(alice), {"from": alice})
        chain.sleep(3600)

    if hasattr(zap, "remove_liquidity_one_coin"):
        for idx in range(n_coins):
            zap.remove_liquidity_one_coin(10 ** underlying_decimals[idx], idx, 0, {"from": alice})
            chain.sleep(3600)
