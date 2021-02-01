import brownie
import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "approve_zap")


@pytest.fixture(scope="module", autouse=True)
def setup(add_initial_liquidity, approve_zap, alice, bob, pool_token):
    pool_token.transfer(bob, pool_token.balanceOf(alice), {"from": alice})


@pytest.mark.parametrize("divisor", [1, 23, 1337])
def test_lp_token_balances(bob, zap, underlying_coins, pool_token, divisor):
    initial_balance = pool_token.balanceOf(bob)
    withdraw_amount = initial_balance // divisor
    min_amounts = [0] * len(underlying_coins)
    zap.remove_liquidity(withdraw_amount, min_amounts, {"from": bob})

    # bob is the only LP, total supply is affected in the same way as his balance
    assert pool_token.balanceOf(bob) == initial_balance - withdraw_amount
    assert pool_token.totalSupply() == initial_balance - withdraw_amount


@pytest.mark.parametrize("divisor", [1, 23, 1337])
def test_wrapped_balances(
    bob, swap, zap, underlying_coins, wrapped_coins, pool_token, initial_amounts, divisor,
):
    initial_balance = pool_token.balanceOf(bob)
    withdraw_amount = initial_balance // divisor
    min_amounts = [0] * len(underlying_coins)
    zap.remove_liquidity(withdraw_amount, min_amounts, {"from": bob})

    for coin, initial in zip(wrapped_coins, initial_amounts):
        assert coin.balanceOf(zap) == 0
        assert coin.balanceOf(swap) == initial - (initial // divisor)


@pytest.mark.parametrize("divisor", [1, 23, 1337])
def test_underlying_balances(
    bob,
    swap,
    zap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    initial_amounts_underlying,
    divisor,
    is_metapool,
):
    initial_balance = pool_token.balanceOf(bob)
    withdraw_amount = initial_balance // divisor
    min_amounts = [0] * len(underlying_coins)
    zap.remove_liquidity(withdraw_amount, min_amounts, {"from": bob})

    expected = [i // divisor for i in initial_amounts_underlying]

    for coin, amount, initial in zip(underlying_coins, expected, initial_amounts_underlying):
        if coin not in wrapped_coins:
            assert coin.balanceOf(swap) == 0
        else:
            assert coin.balanceOf(swap) == initial - amount
        assert coin.balanceOf(zap) == 0

        assert 0.9 < coin.balanceOf(bob) / amount <= 1


@pytest.mark.itercoins("idx")
def test_below_min_amount(alice, zap, initial_amounts_underlying, base_amount, idx):
    n_coins = len(initial_amounts_underlying)
    min_amount = initial_amounts_underlying.copy()
    min_amount[idx] += 1

    amount = n_coins * 10 ** 18 * base_amount
    with brownie.reverts():
        zap.remove_liquidity(amount, min_amount, {"from": alice})


def test_amount_exceeds_balance(alice, zap, underlying_coins, base_amount):
    n_coins = len(underlying_coins)
    amount = n_coins * 10 ** 18 * base_amount + 1
    with brownie.reverts():
        zap.remove_liquidity(amount, [0] * n_coins, {"from": alice})
