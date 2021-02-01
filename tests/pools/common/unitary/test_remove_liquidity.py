import brownie
import pytest
from brownie import ETH_ADDRESS

pytestmark = pytest.mark.usefixtures("add_initial_liquidity")


@pytest.mark.parametrize("min_amount", (0, 1))
def test_remove_liquidity(
    alice, swap, wrapped_coins, pool_token, min_amount, initial_amounts, base_amount, n_coins
):
    swap.remove_liquidity(
        n_coins * 10 ** 18 * base_amount, [i * min_amount for i in initial_amounts], {"from": alice}
    )

    for coin, amount in zip(wrapped_coins, initial_amounts):
        if coin == ETH_ADDRESS:
            assert alice.balance() == amount
            assert swap.balance() == 0
        else:
            assert coin.balanceOf(alice) == amount
            assert coin.balanceOf(swap) == 0

    assert pool_token.balanceOf(alice) == 0
    assert pool_token.totalSupply() == 0


def test_remove_partial(
    alice, swap, wrapped_coins, pool_token, initial_amounts, base_amount, n_coins
):
    withdraw_amount = sum(initial_amounts) // 2
    swap.remove_liquidity(withdraw_amount, [0] * n_coins, {"from": alice})

    for coin, amount in zip(wrapped_coins, initial_amounts):
        if coin == ETH_ADDRESS:
            pool_balance = swap.balance()
            alice_balance = alice.balance()
        else:
            pool_balance = coin.balanceOf(swap)
            alice_balance = coin.balanceOf(alice)
        assert alice_balance + pool_balance == amount

    assert pool_token.balanceOf(alice) == n_coins * 10 ** 18 * base_amount - withdraw_amount
    assert pool_token.totalSupply() == n_coins * 10 ** 18 * base_amount - withdraw_amount


@pytest.mark.itercoins("idx")
def test_below_min_amount(alice, swap, initial_amounts, base_amount, n_coins, idx):
    min_amount = initial_amounts.copy()
    min_amount[idx] += 1

    with brownie.reverts():
        swap.remove_liquidity(n_coins * 10 ** 18 * base_amount, min_amount, {"from": alice})


def test_amount_exceeds_balance(alice, swap, n_coins, base_amount):
    with brownie.reverts():
        swap.remove_liquidity(n_coins * 10 ** 18 * base_amount + 1, [0] * n_coins, {"from": alice})


def test_event(alice, bob, swap, wrapped_coins, pool_token, n_coins):
    pool_token.transfer(bob, 10 ** 18, {"from": alice})
    tx = swap.remove_liquidity(10 ** 18, [0] * n_coins, {"from": bob})

    event = tx.events["RemoveLiquidity"]
    assert event["provider"] == bob
    assert event["token_supply"] == pool_token.totalSupply()
    for coin, amount in zip(wrapped_coins, event["token_amounts"]):
        if coin == ETH_ADDRESS:
            assert tx.internal_transfers[0]["value"] == amount
        else:
            assert coin.balanceOf(bob) == amount
