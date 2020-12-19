import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(add_initial_liquidity, alice, bob, pool_token):
    pool_token.transfer(bob, pool_token.balanceOf(alice), {'from': alice})


@pytest.mark.parametrize("min_amount", (0, 1))
def test_remove_liquidity(bob, swap, underlying_coins, wrapped_coins, pool_token, min_amount, initial_amounts_underlying, base_amount, n_coins):
    swap.remove_liquidity(
        n_coins * 10**18 * base_amount,
        [i * min_amount for i in initial_amounts_underlying],
        True,
        {'from': bob}
    )

    for coin, amount in zip(underlying_coins, initial_amounts_underlying):
        assert coin.balanceOf(bob) == amount
        assert coin.balanceOf(swap) == 0

    for coin in wrapped_coins:
        assert coin.balanceOf(bob) == 0
        assert coin.balanceOf(swap) == 0

    assert pool_token.balanceOf(bob) == 0
    assert pool_token.totalSupply() == 0


def test_remove_partial(bob, swap, underlying_coins, wrapped_coins, pool_token, initial_amounts, initial_amounts_underlying, base_amount, n_coins):
    withdraw_amount = sum(initial_amounts_underlying) // 2
    swap.remove_liquidity(withdraw_amount, [0] * n_coins, True, {'from': bob})

    for underlying, wrapped, amount in zip(underlying_coins, wrapped_coins, initial_amounts):
        assert underlying.balanceOf(swap) == 0
        assert wrapped.balanceOf(bob) == 0

        pool_balance = wrapped.balanceOf(swap)
        bob_balance = underlying.balanceOf(bob)
        assert pool_balance > 0
        assert bob_balance > 0
        assert (bob_balance * 10**18 // 10**underlying.decimals()) + (pool_balance * 10 ** 18 // 10**wrapped.decimals()) == amount

    assert pool_token.balanceOf(bob) == n_coins * 10**18 * base_amount - withdraw_amount
    assert pool_token.totalSupply() == n_coins * 10**18 * base_amount - withdraw_amount


@pytest.mark.itercoins("idx")
def test_below_min_amount(bob, swap, initial_amounts_underlying, base_amount, n_coins, idx):
    min_amount = initial_amounts_underlying.copy()
    min_amount[idx] += 1

    with brownie.reverts():
        swap.remove_liquidity(n_coins * 10**18 * base_amount, min_amount, True, {'from': bob})


def test_amount_exceeds_balance(bob, swap, n_coins, base_amount):
    with brownie.reverts():
        swap.remove_liquidity(n_coins * 10**18 * base_amount + 1, [0] * n_coins, True, {'from': bob})


def test_event(alice, bob, swap, underlying_coins, pool_token, n_coins):
    tx = swap.remove_liquidity(10**18, [0] * n_coins, True, {'from': bob})

    event = tx.events['RemoveLiquidity']
    assert event['provider'] == bob
    assert event['token_supply'] == pool_token.totalSupply()
    for coin, amount in zip(underlying_coins, event['token_amounts']):
        assert coin.balanceOf(bob) == amount * 10**coin.decimals() // 10**18
