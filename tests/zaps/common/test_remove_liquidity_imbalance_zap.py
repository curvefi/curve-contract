import pytest

pytestmark = [
    pytest.mark.usefixtures("add_initial_liquidity", "approve_zap"),
    pytest.mark.skip_meta,
]


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("divisor", [10, 50, 100])
def test_remove_imbalance(
    alice,
    bob,
    swap,
    zap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    idx,
    n_coins,
    initial_amounts,
    divisor,
):
    amounts = [i // divisor for i in initial_amounts]
    max_burn = (n_coins * 10**24) // divisor

    pool_token.transfer(bob, pool_token.balanceOf(alice), {'from': alice})
    zap.remove_liquidity_imbalance(amounts, max_burn + 1, {'from': bob})

    zipped = zip(underlying_coins, wrapped_coins, initial_amounts, amounts)
    for underlying, wrapped, initial, expected in zipped:
        assert underlying.balanceOf(zap) == 0
        assert wrapped.balanceOf(zap) == 0

        assert 0 < underlying.balanceOf(bob) <= expected
        assert wrapped.balanceOf(swap) == initial - expected

    assert abs(pool_token.balanceOf(bob) - (n_coins * 10**24 - max_burn)) <= 1
    assert pool_token.balanceOf(zap) == 0


@pytest.mark.itercoins("idx")
def test_remove_some(
    alice, bob, swap, zap, underlying_coins, wrapped_coins, pool_token, idx, initial_amounts
):
    amounts = [i//2 for i in initial_amounts]
    amounts[idx] = 0

    pool_token.transfer(bob, pool_token.balanceOf(alice), {'from': alice})
    zap.remove_liquidity_imbalance(amounts, 2**256-1, {'from': bob})

    zipped = zip(underlying_coins, wrapped_coins, initial_amounts, amounts)
    for underlying, wrapped, initial, expected in zipped:
        assert underlying.balanceOf(zap) == 0
        assert wrapped.balanceOf(zap) == 0

        if expected:
            assert 0 < underlying.balanceOf(bob) <= expected
            assert wrapped.balanceOf(swap) == initial - expected
        else:
            assert underlying.balanceOf(bob) == 0
            assert wrapped.balanceOf(swap) == initial

    assert pool_token.balanceOf(zap) == 0
