import itertools

import brownie
import pytest
from brownie import ETH_ADDRESS


@pytest.fixture(scope="module", autouse=True)
def setup(mint_alice, approve_alice, mint_bob, approve_bob, set_fees):
    set_fees(4000000, 5000000000, include_meta=True)


def test_add_liquidity_insufficient_balance(
    chain,
    alice,
    bob,
    charlie,
    swap,
    n_coins,
    wrapped_decimals,
    underlying_decimals,
    wrapped_coins,
    underlying_coins,
    initial_amounts,
):
    # attempt to deposit 10x more funds than user has
    amounts = [i * 10 for i in initial_amounts]
    value = initial_amounts[0] if ETH_ADDRESS in wrapped_coins else 0
    with brownie.reverts():
        swap.add_liquidity(amounts, 0, {"from": alice, "value": value})

    # add liquidity balanced
    amounts = [i // 2 for i in initial_amounts]
    value = amounts[0] if ETH_ADDRESS in wrapped_coins else 0
    swap.add_liquidity(amounts, 0, {"from": alice, "value": value})

    # attempt to perform swaps between coins with insufficient funds
    for send, recv in itertools.permutations(range(n_coins), 2):
        amount = initial_amounts[send] // 4
        value = 0 if wrapped_coins[send] != ETH_ADDRESS else amount
        if underlying_coins[send] == ETH_ADDRESS:
            continue
        with brownie.reverts():
            swap.exchange(send, recv, amount, 0, {"from": charlie, "value": value})

    # attempt to perform swaps between coins with insufficient funds
    if hasattr(swap, "exchange_underlying"):
        for send, recv in itertools.permutations(range(n_coins), 2):
            assert underlying_coins[send].balanceOf(charlie) == 0
            amount = initial_amounts[send] // 4
            with brownie.reverts():
                swap.exchange_underlying(send, recv, amount, 0, {"from": charlie})

    # remove liquidity
    with brownie.reverts():
        swap.remove_liquidity(10 ** 18, [0] * n_coins, {"from": charlie})

    # remove liquidity imbalance
    if hasattr(swap, "remove_liquidity_one_coin"):
        for idx in range(n_coins):
            with brownie.reverts():
                swap.remove_liquidity_one_coin(
                    10 ** wrapped_decimals[idx], idx, 0, {"from": charlie}
                )
