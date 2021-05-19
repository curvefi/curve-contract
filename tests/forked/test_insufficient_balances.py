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
    # attempt to deposit more funds than user has
    for idx in range(n_coins):
        amounts = [i // 2 for i in initial_amounts]
        value = amounts[idx] if wrapped_coins[idx] == ETH_ADDRESS else 0
        amounts[idx] = (
            wrapped_coins[idx].balanceOf(alice) + 1
            if wrapped_coins[idx] != ETH_ADDRESS
            else alice.balance() + 1
        )
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
            value = amount - 1
        # charlie doesn't have enough ETH
        if wrapped_coins[send] == ETH_ADDRESS:
            with pytest.raises(ValueError) as e:
                swap.exchange(send, recv, amount, 0, {"from": charlie, "value": value})
            assert "sender doesn't have enough funds to send tx" in str(e.value)
            with brownie.reverts():
                # didn't send any ETH this time soooo tx fails
                swap.exchange(send, recv, amount, 0, {"from": charlie})
        else:
            with brownie.reverts():
                swap.exchange(send, recv, amount, 0, {"from": charlie, "value": value})

    # attempt to perform swaps between coins with insufficient funds
    if hasattr(swap, "exchange_underlying"):
        for send, recv in itertools.permutations(range(n_coins), 2):
            assert underlying_coins[send].balanceOf(charlie) == 0
            amount = initial_amounts[send] // 4
            with brownie.reverts():
                swap.exchange_underlying(send, recv, amount, 0, {"from": charlie})

    # remove liquidity balanced
    with brownie.reverts():
        swap.remove_liquidity(10 ** 18, [0] * n_coins, {"from": charlie})

    # remove liquidity imbalanced
    for idx in range(n_coins):
        amounts = [10 ** wrapped_decimals[i] for i in range(n_coins)]
        amounts[idx] = (
            wrapped_coins[idx].balanceOf(swap) + 1
            if wrapped_coins[idx] != ETH_ADDRESS
            else swap.balance() + 1
        )
        with brownie.reverts():
            swap.remove_liquidity_imbalance(
                amounts, 2 ** 256 - 1, {"from": charlie, "value": value}
            )

    if hasattr(swap, "remove_liquidity_one_coin"):
        for idx in range(n_coins):
            with brownie.reverts():
                swap.remove_liquidity_one_coin(
                    10 ** wrapped_decimals[idx], idx, 0, {"from": charlie}
                )
