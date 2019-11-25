import time
import pytest
import random
from itertools import permutations
from .conftest import UU
from .simulation import Curve


@pytest.mark.parametrize('n_coins', [100, 10 ** 6, 10 ** 9])
def test_curve_in_contract(w3, coins, swap, n_coins):
    # Allow $1000 of each coin
    for c, u in zip(coins, UU):
        c.functions.approve(swap.address, n_coins * 10 * u).\
                transact({'from': w3.eth.accounts[0]})

    # Add some coins
    swap.functions.\
        add_liquidity([n_coins * u for u in UU], int(time.time()) + 3600).\
        transact({'from': w3.eth.accounts[0]})

    # Python-based (tested) model with same parameters as contract
    curve = Curve(2 * 360, 3 * n_coins * max(UU), 3)

    for k in range(5):
        for i, j in permutations(range(3), 2):
            dx = random.randrange(2 * n_coins * UU[i])
            dy_1 = swap.caller.get_dy(i, j, dx)
            dy_2 = curve.dy(i, j, dx)
            assert dy_1 == dy_2
