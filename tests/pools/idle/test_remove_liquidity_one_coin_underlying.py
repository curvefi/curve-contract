import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(add_initial_liquidity, alice, bob, pool_token):
    pool_token.transfer(bob, pool_token.balanceOf(alice), {'from': alice})


@pytest.mark.itercoins("idx")
def test_amount_received(chain, bob, swap, underlying_coins, wrapped_coins, idx):

    wrapped = wrapped_coins[idx]
    underlying = underlying_coins[idx]

    initial = wrapped.balanceOf(swap)

    swap.remove_liquidity_one_coin(10**18, idx, 0, True, {'from': bob})

    assert 0.9999 < underlying.balanceOf(bob) / 10**underlying.decimals() < 1
    assert wrapped.balanceOf(swap) + 10**wrapped.decimals() > initial


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("divisor", [1, 5, 42])
def test_lp_token_balance(bob, swap, pool_token, idx, divisor, n_coins, base_amount):
    amount = pool_token.balanceOf(bob) // divisor

    swap.remove_liquidity_one_coin(amount, idx, 0, True, {'from': bob})

    assert pool_token.balanceOf(bob) == n_coins * 10**18 * base_amount - amount


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("rate_mod", [0.9, 1.1])
def test_expected_vs_actual(chain, bob, swap, underlying_coins, pool_token, idx, rate_mod):
    amount = pool_token.balanceOf(bob) // 10

    expected = swap.calc_withdraw_one_coin(amount, idx, True)
    swap.remove_liquidity_one_coin(amount, idx, 0, True, {'from': bob})

    assert underlying_coins[idx].balanceOf(bob) == expected


@pytest.mark.itercoins("idx")
def test_below_min_amount(bob, swap, wrapped_coins, pool_token, idx):
    amount = pool_token.balanceOf(bob)

    expected = swap.calc_withdraw_one_coin(amount, idx, True)
    with brownie.reverts():
        swap.remove_liquidity_one_coin(amount, idx, expected+1, True, {'from': bob})


@pytest.mark.itercoins("idx")
def test_amount_exceeds_balance(bob, swap, wrapped_coins, pool_token, idx):
    with brownie.reverts():
        swap.remove_liquidity_one_coin(pool_token.balanceOf(bob) + 1, idx, 0, True, {'from': bob})


@pytest.mark.itercoins("idx")
def test_event(alice, bob, swap, pool_token, idx, wrapped_decimals):
    tx = swap.remove_liquidity_one_coin(10**18, idx, 0, True, {'from': bob})

    event = tx.events["RemoveLiquidityOne"]
    assert event['provider'] == bob
    assert event['token_amount'] == 10**18
    assert 0.9999 < event['coin_amount'] / 10**wrapped_decimals[idx] < 1
