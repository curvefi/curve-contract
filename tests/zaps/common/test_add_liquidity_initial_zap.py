import brownie
import pytest

pytestmark = pytest.mark.usefixtures("mint_alice", "approve_zap")


@pytest.mark.parametrize("min_amount", (False, True))
def test_initial(
    alice,
    zap,
    swap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    underlying_decimals,
    n_coins,
    initial_amounts,
    min_amount,
):
    amounts = [10**i for i in underlying_decimals]
    min_amount = 10**18 * n_coins if min_amount else 0

    zap.add_liquidity(amounts, min_amount, {'from': alice})

    zipped = zip(underlying_coins, wrapped_coins, amounts, initial_amounts)
    for underlying, wrapped, amount, initial in zipped:
        assert underlying.balanceOf(alice) == initial - amount

        if wrapped == underlying:
            assert underlying.balanceOf(zap) == 0
            assert underlying.balanceOf(swap) == amount
        else:
            assert underlying.balanceOf(zap) == 0
            assert underlying.balanceOf(swap) == 0
            assert wrapped.balanceOf(alice) == initial
            assert wrapped.balanceOf(zap) == 0
            assert wrapped.balanceOf(swap) == amount

    assert pool_token.balanceOf(alice) == n_coins * 10**18
    assert pool_token.totalSupply() == n_coins * 10**18


@pytest.mark.itercoins("idx")
def test_initial_liquidity_missing_coin(alice, zap, pool_token, idx, underlying_decimals):
    amounts = [10**i for i in underlying_decimals]
    amounts[idx] = 0

    with brownie.reverts():
        zap.add_liquidity(amounts, 0, {'from': alice})
