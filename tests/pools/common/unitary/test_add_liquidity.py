import brownie
import pytest
from brownie import ETH_ADDRESS

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_bob")


def test_add_liquidity(bob, swap, wrapped_coins, pool_token, initial_amounts, base_amount, n_coins):
    value = initial_amounts[0] if ETH_ADDRESS in wrapped_coins else 0
    swap.add_liquidity(initial_amounts, 0, {"from": bob, "value": value})

    for coin, amount in zip(wrapped_coins, initial_amounts):
        if coin == ETH_ADDRESS:
            assert bob.balance() == 0
            assert swap.balance() == amount * 2
        else:
            assert coin.balanceOf(bob) == 0
            assert coin.balanceOf(swap) == amount * 2

    assert pool_token.balanceOf(bob) == n_coins * 10 ** 18 * base_amount
    assert pool_token.totalSupply() == n_coins * 10 ** 18 * base_amount * 2


def test_add_with_slippage(bob, swap, pool_token, wrapped_decimals, wrapped_coins, n_coins):
    amounts = [10 ** i for i in wrapped_decimals]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    value = amounts[0] if ETH_ADDRESS in wrapped_coins else 0

    swap.add_liquidity(amounts, 0, {"from": bob, "value": value})

    assert 0.999 < pool_token.balanceOf(bob) / (n_coins * 10 ** 18) < 1


@pytest.mark.itercoins("idx")
def test_add_one_coin(
    bob, swap, wrapped_coins, pool_token, initial_amounts, base_amount, idx, n_coins
):
    amounts = [0] * n_coins
    amounts[idx] = initial_amounts[idx]
    value = amounts[0] if ETH_ADDRESS in wrapped_coins else 0

    swap.add_liquidity(amounts, 0, {"from": bob, "value": value})

    for i, coin in enumerate(wrapped_coins):
        if coin == ETH_ADDRESS:
            assert bob.balance() + amounts[i] == initial_amounts[i]
            assert swap.balance() == initial_amounts[i] + amounts[i]
        else:
            assert coin.balanceOf(bob) == initial_amounts[i] - amounts[i]
            assert coin.balanceOf(swap) == initial_amounts[i] + amounts[i]

    assert 0.999 < pool_token.balanceOf(bob) / (10 ** 18 * base_amount) < 1


def test_insufficient_balance(charlie, swap, wrapped_decimals):
    amounts = [(10 ** i) for i in wrapped_decimals]

    with brownie.reverts():
        swap.add_liquidity(amounts, 0, {"from": charlie})


def test_min_amount_too_high(bob, swap, wrapped_decimals, wrapped_coins, n_coins):
    amounts = [10 ** i for i in wrapped_decimals]
    value = amounts[0] if ETH_ADDRESS in wrapped_coins else 0

    min_amount = (10 ** 18 * n_coins) + 1
    with brownie.reverts():
        swap.add_liquidity(amounts, min_amount, {"from": bob, "value": value})


def test_min_amount_with_slippage(bob, swap, wrapped_decimals, wrapped_coins, n_coins):
    amounts = [10 ** i for i in wrapped_decimals]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    value = amounts[0] if ETH_ADDRESS in wrapped_coins else 0

    with brownie.reverts("Slippage screwed you"):
        swap.add_liquidity(amounts, n_coins * 10 ** 18, {"from": bob, "value": value})


def test_event(bob, swap, pool_token, initial_amounts, wrapped_coins):
    value = initial_amounts[0] if ETH_ADDRESS in wrapped_coins else 0
    tx = swap.add_liquidity(initial_amounts, 0, {"from": bob, "value": value})

    event = tx.events["AddLiquidity"]
    assert event["provider"] == bob
    assert event["token_amounts"] == initial_amounts
    assert event["token_supply"] == pool_token.totalSupply()


def test_wrong_eth_amount(bob, swap, wrapped_coins, pool_token, initial_amounts, n_coins):
    # for ETH pools, tests sending too much ETH
    # for non-ETH pools, tests that function is nonpayable
    value = initial_amounts[0] - 1 if ETH_ADDRESS in wrapped_coins else 1
    with brownie.reverts():
        swap.add_liquidity(initial_amounts, 0, {"from": bob, "value": value})
