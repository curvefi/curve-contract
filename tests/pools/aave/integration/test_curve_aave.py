from collections import deque
from itertools import permutations

import pytest
from brownie.test import given, strategy
from hypothesis import settings
from simulation import Curve

pytestmark = pytest.mark.skip_pool_type("meta")


@given(
    st_pct=strategy("decimal[50]", min_value="0.001", max_value=1, unique=True, places=3),
    st_seed_amount=strategy("decimal", min_value=5, max_value=12, places=1),
)
@settings(max_examples=5)
def test_curve_in_contract(
    alice, swap, wrapped_coins, st_seed_amount, n_coins, approx, st_pct, wrapped_decimals
):
    st_seed_amount = int(10 ** st_seed_amount)

    # add initial pool liquidity
    # we add at an imbalance of +10% for each subsequent coin
    initial_liquidity = []
    for coin, decimals in zip(wrapped_coins, wrapped_decimals):
        amount = st_seed_amount * 10 ** decimals + 1
        amount = int(amount * (1 + 0.1 * len(initial_liquidity)))
        coin._mint_for_testing(alice, amount, {"from": alice})

        assert coin.balanceOf(alice) >= amount
        initial_liquidity.append(amount // 10)
        coin.approve(swap, amount // 10, {"from": alice})

    swap.add_liquidity(initial_liquidity, 0, {"from": alice})

    # initialize our python model using the same parameters as the contract
    balances = [swap.balances(i) for i in range(n_coins)]
    rates = []
    for decimals in wrapped_decimals:
        rate = 10 ** 18
        precision = 10 ** (18 - decimals)
        rates.append(rate * precision)
    curve_model = Curve(2 * 360, balances, n_coins, rates)

    # execute a series of swaps and compare the python model to the contract results
    rates = [10 ** 18 for i in range(n_coins)]
    exchange_pairs = deque(permutations(range(n_coins), 2))

    while st_pct:
        exchange_pairs.rotate()
        send, recv = exchange_pairs[0]
        dx = int(2 * st_seed_amount * 10 ** wrapped_decimals[send] * st_pct.pop())

        dy_1_c = swap.get_dy(send, recv, dx)
        dy_1_u = swap.get_dy_underlying(send, recv, dx)
        assert dy_1_u == dy_1_c

        dy_2 = curve_model.dy(send, recv, dx * (10 ** (18 - wrapped_decimals[send])))
        dy_2 //= 10 ** (18 - wrapped_decimals[recv])

        assert approx(dy_1_c, dy_2, 1e-8) or abs(dy_1_c - dy_2) <= 2
