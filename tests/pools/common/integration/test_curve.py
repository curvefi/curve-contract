import pytest

from brownie.test import given, strategy
from collections import deque
from hypothesis import settings
from itertools import permutations
from simulation import Curve

pytestmark = pytest.mark.skip_meta


@given(
    st_pct=strategy('decimal[50]', min_value="0.001", max_value=1, unique=True, places=3),
    st_seed_amount=strategy("decimal", min_value=5, max_value=12, places=1)
)
@settings(max_examples=5)
def test_curve_in_contract(
    alice, swap, underlying_coins, wrapped_coins, st_seed_amount, pool_data, n_coins, approx, st_pct
):
    coin_data = pool_data['coins']
    st_seed_amount = int(10 ** st_seed_amount)

    # add initial pool liquidity
    # we add at an imbalance of +10% for each subsequent coin
    initial_liquidity = []
    for underlying, wrapped, data in zip(underlying_coins, wrapped_coins, coin_data):
        amount = st_seed_amount * 10 ** (data['decimals'] + 1)
        underlying._mint_for_testing(alice, amount, {'from': alice})

        if data['wrapped']:
            rate = int(10**18 * (1 + 0.1 * len(initial_liquidity)))
            wrapped.set_exchange_rate(rate, {'from': alice})
            underlying.approve(wrapped, amount, {'from': alice})
            wrapped.mint(amount, {'from': alice})
            amount = amount * 10 ** 18 // rate

        assert wrapped.balanceOf(alice) >= amount
        initial_liquidity.append(amount // 10)
        wrapped.approve(swap, amount // 10, {'from': alice})

    swap.add_liquidity(initial_liquidity, 0, {'from': alice})

    # initialize our python model using the same parameters as the contract
    balances = [swap.balances(i) for i in range(n_coins)]
    rates = []
    for (coin, data) in zip(wrapped_coins, pool_data['coins']):
        if data['wrapped']:
            rate = coin.get_rate()
        else:
            rate = 10 ** 18

        precision = 10 ** (18-data['decimals'])
        rates.append(rate * precision)
    curve_model = Curve(2 * 360, balances, n_coins, rates)

    # execute a series of swaps and compare the python model to the contract results
    rates = [
        wrapped_coins[i].get_rate() if coin_data[i]['wrapped']
        else 10 ** 18 for i in range(n_coins)
    ]
    exchange_pairs = deque(permutations(range(n_coins), 2))

    while st_pct:
        exchange_pairs.rotate()
        send, recv = exchange_pairs[0]
        dx = int(2 * st_seed_amount * 10 ** coin_data[send]['decimals'] * st_pct.pop())

        dx_c = dx * 10 ** 18 // rates[send]

        dy_1_c = swap.get_dy(send, recv, dx_c)

        if hasattr(swap, "get_dy_underlying"):
            dy_1_u = swap.get_dy_underlying(send, recv, dx)
        else:
            dy_1_u = dy_1_c

        dy_1 = dy_1_c * rates[recv] // 10 ** 18

        dy_2 = curve_model.dy(send, recv, dx * (10 ** (18 - coin_data[send]['decimals'])))
        dy_2 //= (10 ** (18 - coin_data[recv]['decimals']))

        assert approx(dy_1, dy_2, 1e-8) or abs(dy_1 - dy_2) <= 2
        assert approx(dy_1_u, dy_2, 1e-8) or abs(dy_1 - dy_2) <= 2
