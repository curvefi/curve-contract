import pytest
import random
from itertools import permutations
from .conftest import UU, PRECISIONS, approx
from .simulation import Curve


@pytest.mark.parametrize('n_coins', [100, 10 ** 6, 10 ** 9])
def test_curve_in_contract(w3, coins, swap, n_coins):
    alice = w3.eth.accounts[0]
    from_alice = {'from': alice}

    # Prepare x10 of each coin
    n_ccoins = []
    for c, u in zip(coins, UU):
        # Set price to non-1.0: 1.0, 1.1 and 1.2
        n = n_coins * 10 * u
        n_ccoins.append(n)
        assert c.caller.balanceOf(alice) >= n
        c.functions.approve(swap.address, n // 10).transact(from_alice)

    # Add some coins
    swap.functions.\
        add_liquidity([n // 10 for n in n_ccoins], 0).\
        transact(from_alice)

    # Python-based (tested) model with same parameters as contract
    balances = [int(swap.caller.balances(i)) for i in range(3)]
    curve = Curve(2 * 360, balances, 3, [p * 10 ** 18 for p in PRECISIONS])

    for k in range(5):
        for i, j in permutations(range(3), 2):
            dx = random.randrange(2 * n_coins * UU[i])
            dy_1 = swap.caller.get_dy(i, j, dx)
            dy_2 = curve.dy(i, j, dx * PRECISIONS[i]) // PRECISIONS[j]
            dy_2 = dy_2 * 999 // 1000  # Account for fee
            assert approx(dy_1, dy_2, 1e-8) or abs(dy_1 - dy_2) <= 2
