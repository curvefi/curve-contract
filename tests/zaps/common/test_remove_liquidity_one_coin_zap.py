import brownie
import pytest

# old deployments are skipped because of a known issue with dust

pytestmark = [
    pytest.mark.usefixtures("add_initial_liquidity", "approve_zap"),
    pytest.mark.skip_pool("busd", "compound", "pax", "susd", "usdt", "y"),
]


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("divisor", [10, 50, 100])
def test_remove_one(alice, bob, zap, underlying_coins, wrapped_coins, pool_token, idx, divisor):
    underlying = underlying_coins[idx]
    wrapped = wrapped_coins[idx]

    initial_amount = pool_token.balanceOf(alice)
    amount = initial_amount // divisor

    pool_token.transfer(bob, initial_amount, {"from": alice})
    zap.remove_liquidity_one_coin(amount, idx, 0, {"from": bob})

    assert underlying.balanceOf(zap) == 0
    assert wrapped.balanceOf(zap) == 0
    assert pool_token.balanceOf(zap) == 0

    if wrapped != underlying:
        assert wrapped.balanceOf(bob) == 0

    assert pool_token.balanceOf(bob) == initial_amount - amount
    assert 0 < underlying.balanceOf(bob) <= amount


@pytest.mark.itercoins("idx")
def test_amount_exceeds_balance(bob, zap, idx):
    with brownie.reverts():
        zap.remove_liquidity_one_coin(1, idx, 0, {"from": bob})
