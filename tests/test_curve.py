import time
import random
from itertools import permutations
from simulation import Curve

U = 10 ** 18


def test_curve_in_contract(w3, coins, swap):
    # Allow $1000 of each coin
    for c in coins:
        c.approve(swap.address, 1000 * U,
                  transact={'from': w3.eth.accounts[0]})

    # Add some coins
    swap.add_liquidity(0, 100 * U, 110 * U, int(time.time()) + 3600,
                       transact={'from': w3.eth.accounts[0]})

    # Python-based (tested) model with same parameters as contract
    curve = Curve(2 * 360, 300 * U, 3)

    for i, j in permutations(range(3), 2):
        dx = random.randrange(100 * U)
        dy_1 = swap.get_dy(i, j, dx)
        dy_2 = curve.dy(i, j, dx)
        assert dy_1 == dy_2
