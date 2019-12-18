import time
import pytest
import random
from itertools import permutations
from .conftest import UU, PRECISIONS
from .simulation import Curve


@pytest.mark.parametrize('n_coins', [100, 10 ** 6, 10 ** 9])
def test_curve_in_contract(w3, coins, cerc20s, swap, n_coins):
    alice = w3.eth.accounts[0]
    from_alice = {'from': alice}

    # Prepare x10 of each coin
    n_ccoins = []
    for c, cc, u in zip(coins, cerc20s, UU):
        c.functions.approve(cc.address, n_coins * 10 * u).transact(from_alice)
        cc.functions.mint(n_coins * 10 * u).transact(from_alice)
        rate = cc.caller.exchangeRateStored()
        n = n_coins * 10 * u * 10 ** 18 // rate
        n_ccoins.append(n)
        assert cc.caller.balanceOf(alice) == n
        cc.functions.approve(swap.address, n // 10).transact(from_alice)

    # Add some coins
    swap.functions.\
        add_liquidity([n // 10 for n in n_ccoins], int(time.time()) + 3600).\
        transact(from_alice)

    # Python-based (tested) model with same parameters as contract
    curve = Curve(2 * 360, 3 * n_coins * max(UU), 3)

    for k in range(5):
        for i, j in permutations(range(3), 2):
            dx = random.randrange(2 * n_coins * UU[i])
            rate_x = cerc20s[i].caller.exchangeRateStored()
            dx_c = dx * 10 ** 18 // rate_x
            dy_1_c = swap.caller.get_dy(i, j, dx_c)
            dy_2 = curve.dy(i, j, dx * PRECISIONS[i]) // PRECISIONS[j]
            rate_y = cerc20s[j].caller.exchangeRateStored()
            if rate_y < 10 ** 18:  # condition to avoid rounding off error
                dy_1 = dy_1_c * rate_y // 10 ** 18
                assert dy_1 == dy_2
            else:
                dy_2_c = dy_2 * 10 ** 18 // rate_y
                assert dy_1_c == dy_2_c
