import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, pool_token, add_initial_liquidity, approve_zap):
    pool_token.transfer(bob, pool_token.balanceOf(alice), {"from": alice})


@pytest.mark.parametrize("divisor", [2, 7, 31337])
def test_lp_token_balances(
    bob, zap, pool_token, divisor, initial_amounts_underlying, base_amount, n_coins
):
    amounts = [i // divisor for i in initial_amounts_underlying]
    max_burn = (n_coins * 10 ** 18 * base_amount) // divisor + 1

    initial_balance = pool_token.balanceOf(bob)
    zap.remove_liquidity_imbalance(amounts, max_burn, {"from": bob})

    # bob is the only LP, total supply is affected in the same way as his balance
    assert pool_token.balanceOf(bob) < initial_balance
    assert pool_token.balanceOf(bob) >= initial_balance - max_burn

    assert pool_token.balanceOf(zap) == 0
    assert pool_token.balanceOf(bob) == pool_token.totalSupply()


@pytest.mark.parametrize("divisor", [2, 7, 31337])
def test_wrapped_balances(
    bob,
    swap,
    zap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    initial_amounts,
    initial_amounts_underlying,
    base_amount,
    divisor,
    n_coins,
):
    amounts = [i // divisor for i in initial_amounts_underlying]
    max_burn = (n_coins * 10 ** 18 * base_amount) // divisor
    zap.remove_liquidity_imbalance(amounts, max_burn + 1, {"from": bob})

    for coin, initial in zip(wrapped_coins, initial_amounts):
        assert coin.balanceOf(zap) == 0
        assert 0.99 < (initial - (initial // divisor)) / coin.balanceOf(swap) <= 1


@pytest.mark.parametrize("divisor", [2, 7, 31337])
@pytest.mark.parametrize("is_inclusive", [True, False])
@pytest.mark.itercoins("idx", underlying=True)
def test_underlying_balances(
    bob,
    swap,
    zap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    initial_amounts_underlying,
    base_amount,
    divisor,
    idx,
    is_inclusive,
    n_coins,
):
    if is_inclusive:
        amounts = [i // divisor for i in initial_amounts_underlying]
        amounts[idx] = 0
    else:
        amounts = [0] * len(initial_amounts_underlying)
        amounts[idx] = initial_amounts_underlying[idx] // divisor
    max_burn = (n_coins * 10 ** 18 * base_amount) // divisor
    zap.remove_liquidity_imbalance(amounts, max_burn + 1, {"from": bob})

    for coin, amount, initial in zip(underlying_coins, amounts, initial_amounts_underlying):
        if coin not in wrapped_coins:
            assert coin.balanceOf(swap) == 0
        else:
            assert coin.balanceOf(swap) == initial - amount
        assert coin.balanceOf(zap) == 0

        if amount:
            assert 0.9 < coin.balanceOf(bob) / amount <= 1
        else:
            assert coin.balanceOf(bob) == 0
