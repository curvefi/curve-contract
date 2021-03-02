import pytest

pytestmark = [
    pytest.mark.skip_pool("busd", "compound", "pax", "susd", "usdt", "y"),
    pytest.mark.usefixtures("add_initial_liquidity", "approve_zap"),
]


def test_remove_liquidity(alice, bob, zap, pool_token, underlying_coins, base_amount):
    n_coins = len(underlying_coins)
    pool_token.transfer(bob, pool_token.balanceOf(alice), {"from": alice})
    tx = zap.remove_liquidity(n_coins * 10 ** 18 * base_amount // 3, [0] * n_coins, {"from": bob})
    for coin, expected_amount in zip(underlying_coins, tx.return_value):
        assert coin.balanceOf(bob) == expected_amount


@pytest.mark.skip_pool_type("meta")
def test_remove_imbalance(
    alice, bob, zap, initial_amounts_underlying, pool_token, underlying_coins
):
    amounts = [i // 2 for i in initial_amounts_underlying]
    amounts[0] = 0

    pool_token.transfer(bob, pool_token.balanceOf(alice), {"from": alice})
    tx = zap.remove_liquidity_imbalance(amounts, 2 ** 256 - 1, {"from": bob})
    for coin, expected_amount in zip(underlying_coins, tx.return_value):
        assert coin.balanceOf(bob) == expected_amount


def test_remove_one(alice, bob, zap, underlying_coins, wrapped_coins, pool_token):
    pool_token.transfer(bob, pool_token.balanceOf(alice), {"from": alice})
    tx = zap.remove_liquidity_one_coin(10 ** 18, 1, 0, {"from": bob})

    assert tx.return_value == underlying_coins[1].balanceOf(bob)


def test_add_liquidity(bob, zap, initial_amounts_underlying, pool_token, mint_bob):
    tx = zap.add_liquidity(initial_amounts_underlying, 0, {"from": bob})
    assert pool_token.balanceOf(bob) == tx.return_value
