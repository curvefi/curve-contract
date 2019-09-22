import time
import pytest
import random
from itertools import permutations
from simulation import Curve

U = 10 ** 18


@pytest.mark.parametrize('n_coins', [100, 10 ** 6, 10 ** 9])
def test_curve_in_contract(w3, coins, swap, n_coins):
    # Allow $1000 of each coin
    for c in coins:
        c.approve(swap.address, n_coins * 10 * U,
                  transact={'from': w3.eth.accounts[0]})

    # Add some coins
    swap.add_liquidity(0, n_coins * U, 2 * n_coins * U, int(time.time()) + 3600,
                       transact={'from': w3.eth.accounts[0]})

    # Python-based (tested) model with same parameters as contract
    curve = Curve(2 * 360, 3 * n_coins * U, 3)

    for k in range(5):
        for i, j in permutations(range(3), 2):
            dx = random.randrange(2 * n_coins * U)
            dy_1 = swap.get_dy(i, j, dx)
            dy_2 = curve.dy(i, j, dx)
            assert abs(dy_1 - dy_2) <= 1
