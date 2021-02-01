import brownie
import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_zap")


def test_lp_token_balances(
    bob, zap, swap, pool_token, base_pool_token, initial_amounts_underlying, base_amount, n_coins
):
    initial_supply = pool_token.totalSupply()
    zap.add_liquidity(initial_amounts_underlying, 0, {"from": bob})

    assert 0.9999 < pool_token.balanceOf(bob) / (n_coins * 10 ** 18 * base_amount) <= 1
    assert 0.9999 < (pool_token.totalSupply() / 2) / initial_supply <= 1


def test_underlying_balances(
    bob, zap, swap, underlying_coins, wrapped_coins, initial_amounts_underlying
):
    zap.add_liquidity(initial_amounts_underlying, 0, {"from": bob})

    for coin, amount in zip(underlying_coins, initial_amounts_underlying):
        assert coin.balanceOf(zap) == 0
        if coin in wrapped_coins:
            assert coin.balanceOf(swap) == amount * 2
        else:
            assert coin.balanceOf(swap) == 0


def test_wrapped_balances(
    bob, zap, swap, wrapped_coins, initial_amounts_underlying, initial_amounts
):
    zap.add_liquidity(initial_amounts_underlying, 0, {"from": bob})

    for coin, amount in zip(wrapped_coins, initial_amounts):
        assert coin.balanceOf(zap) == 0
        assert 0.9999 < coin.balanceOf(swap) / (amount * 2) <= 1


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("mod", [0.95, 1.05])
def test_slippage(
    bob, zap, pool_token, underlying_coins, wrapped_coins, initial_amounts_underlying, idx, mod
):
    amounts = [i // 10 ** 6 for i in initial_amounts_underlying]
    amounts[idx] = int(amounts[idx] * mod)

    zap.add_liquidity(amounts, 0, {"from": bob})

    for coin in underlying_coins + wrapped_coins:
        assert coin.balanceOf(zap) == 0

    assert pool_token.balanceOf(zap) == 0


@pytest.mark.itercoins("idx")
def test_add_one_coin(
    bob, swap, zap, underlying_coins, wrapped_coins, underlying_decimals, pool_token, idx
):

    amounts = [0] * len(underlying_decimals)
    amounts[idx] = 10 ** underlying_decimals[idx]
    zap.add_liquidity(amounts, 0, {"from": bob})

    for coin in underlying_coins + wrapped_coins:
        assert coin.balanceOf(zap) == 0

    assert pool_token.balanceOf(zap) == 0
    assert 0.999 < pool_token.balanceOf(bob) / 10 ** 18 < 1


def test_insufficient_balance(charlie, zap, underlying_decimals):
    amounts = [(10 ** i) for i in underlying_decimals]
    with brownie.reverts():
        zap.add_liquidity(amounts, 0, {"from": charlie})


@pytest.mark.parametrize("min_amount", [False, True])
def test_min_amount_too_high(alice, zap, initial_amounts_underlying, min_amount, n_coins):
    amounts = [i // 10 ** 6 for i in initial_amounts_underlying]
    min_amount = n_coins * 10 ** 18 + 1 if min_amount else 2 ** 256 - 1
    with brownie.reverts():
        zap.add_liquidity(amounts, min_amount, {"from": alice})


def test_min_amount_with_slippage(bob, zap, initial_amounts_underlying, n_coins):
    amounts = [i // 10 ** 6 for i in initial_amounts_underlying]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    with brownie.reverts():
        zap.add_liquidity(amounts, n_coins * 10 ** 18, {"from": bob})
