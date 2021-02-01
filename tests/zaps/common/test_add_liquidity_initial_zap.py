import brownie
import pytest

pytestmark = pytest.mark.usefixtures("mint_bob", "approve_zap")


def test_lp_token_balances(
    bob, zap, swap, pool_token, base_pool_token, initial_amounts_underlying, base_amount, n_coins
):
    zap.add_liquidity(initial_amounts_underlying, 0, {"from": bob})

    assert 0.9999 < pool_token.balanceOf(bob) / (n_coins * 10 ** 18 * base_amount) <= 1
    assert pool_token.totalSupply() == pool_token.balanceOf(bob)


def test_underlying_balances(
    bob, zap, swap, underlying_coins, wrapped_coins, initial_amounts_underlying
):
    zap.add_liquidity(initial_amounts_underlying, 0, {"from": bob})

    for coin, amount in zip(underlying_coins, initial_amounts_underlying):
        assert coin.balanceOf(zap) == 0
        if coin in wrapped_coins:
            assert coin.balanceOf(swap) == amount
        else:
            assert coin.balanceOf(swap) == 0


def test_wrapped_balances(
    bob, zap, swap, wrapped_coins, initial_amounts_underlying, initial_amounts
):
    zap.add_liquidity(initial_amounts_underlying, 0, {"from": bob})

    for coin, amount in zip(wrapped_coins, initial_amounts):
        assert coin.balanceOf(zap) == 0
        assert 0.9999 < coin.balanceOf(swap) / amount <= 1


@pytest.mark.skip_pool("template-meta")
@pytest.mark.itercoins("idx")
def test_initial_liquidity_missing_coin(alice, zap, pool_token, idx, underlying_decimals):
    amounts = [10 ** i for i in underlying_decimals]
    amounts[idx] = 0

    with brownie.reverts():
        zap.add_liquidity(amounts, 0, {"from": alice})
