import pytest
from brownie.test import given, strategy
from hypothesis import settings
from simulation import Curve

# do not run this test on pools without lending or meta pools
pytestmark = [pytest.mark.lending, pytest.mark.skip_meta]


@given(
    st_coin=strategy("decimal[100]", min_value=0, max_value="0.99", unique=True, places=2),
    st_divisor=strategy("uint[50]", min_value=1, max_value=100, unique=True),
)
@settings(max_examples=5)
def test_simulated_exchange(
    chain,
    alice,
    bob,
    underlying_coins,
    wrapped_coins,
    wrapped_decimals,
    swap,
    pool_data,
    n_coins,
    set_fees,
    st_coin,
    st_divisor,
):
    """
    Perform a series of token swaps and compare the resulting amounts and pool balances
    with those in our python-based model.

    Strategies
    ----------
    st_coin : decimal[100]
        Array of decimal values, used to choose the coins used in each swap
    st_divisor: uint[50]
        Array of integers, used to choose the size of each swap
    """

    set_fees(10 ** 7, 0)

    # add initial pool liquidity
    initial_liquidity = []
    for underlying, decimals in zip(underlying_coins, wrapped_decimals):
        amount = 1000 * 10 ** decimals
        underlying._mint_for_testing(alice, amount, {"from": alice})
        underlying.approve(swap, amount, {"from": alice})
        initial_liquidity.append(amount // 10)

    swap.add_liquidity(initial_liquidity, 0, True, {"from": alice})

    # initialize our python model using the same parameters as the contract
    balances = [swap.balances(i) for i in range(n_coins)]
    rates = []
    for decimals in wrapped_decimals:
        rate = 10 ** 18
        precision = 10 ** (18 - decimals)
        rates.append(rate * precision)
    curve_model = Curve(2 * 360, balances, n_coins, rates)

    for coin, decimals in zip(underlying_coins, wrapped_decimals):
        # Fund bob with $100 of each coin and approve swap contract
        amount = 100 * 10 ** decimals
        coin._mint_for_testing(bob, amount, {"from": alice})
        coin.approve(swap, amount, {"from": bob})

    # Start trading!
    rate_mul = [10 ** i for i in wrapped_decimals]
    while st_coin:
        # Increase aToken balances by 1% to simulate accrued interest
        for i, coin in enumerate(wrapped_coins):
            coin._mint_for_testing(swap, coin.balanceOf(swap) // 100, {"from": alice})
            curve_model.x[i] = int(curve_model.x[i] * 1.01)

        # Simulate the exchange
        old_virtual_price = swap.get_virtual_price()

        # choose which coins to swap
        send, recv = [int(st_coin.pop() * n_coins) for _ in range(2)]
        if send == recv:
            # if send and recv are the same, adjust send
            send = abs(send - 1)

        value = 5 * rate_mul[send] // st_divisor.pop()

        x_0 = underlying_coins[send].balanceOf(bob)
        y_0 = underlying_coins[recv].balanceOf(bob)
        underlying_coins[send].approve(swap, 0, {"from": bob})
        underlying_coins[send].approve(swap, value, {"from": bob})

        amount = int(0.5 * value * rate_mul[recv] / rate_mul[send])
        swap.exchange_underlying(send, recv, value, amount, {"from": bob})

        x_1 = underlying_coins[send].balanceOf(bob)
        y_1 = underlying_coins[recv].balanceOf(bob)

        dy_m = curve_model.exchange(send, recv, value * max(rate_mul) // rate_mul[send])
        dy_m = dy_m * rate_mul[recv] // max(rate_mul)

        assert x_0 - x_1 == value
        assert (y_1 - y_0) - dy_m <= dy_m * 1e-10
        assert swap.get_virtual_price() > old_virtual_price
        assert wrapped_coins[send].balanceOf(swap) >= swap.balances(send)
        assert wrapped_coins[recv].balanceOf(swap) >= swap.balances(recv)

    # Final assertions - let's see what we have left
    final_balances = [swap.balances(i) for i in range(n_coins)]
    final_total = sum(final_balances[i] * rates[i] / 1e18 for i in range(n_coins))

    assert [round(a / b, 6) for a, b in zip(final_balances, curve_model.x)] == [1.0] * n_coins
    assert final_total > n_coins * 100 * max(rate_mul)
