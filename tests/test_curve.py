import pytest
import random
from itertools import permutations
from .conftest import UU, PRECISIONS, use_lending, approx
from .simulation import Curve


@pytest.mark.parametrize('n_coins', [100, 10 ** 6, 10 ** 9])
def test_curve_in_contract(w3, coins, cerc20s, swap, n_coins):
    alice = w3.eth.accounts[0]
    from_alice = {'from': alice}

    # Prepare x10 of each coin
    n_ccoins = []
    for c, cc, u, l in zip(coins, cerc20s, UU, use_lending):
        # Set price to non-1.0: 1.0, 1.1 and 1.2
        if l:
            rate = int(cc.caller.exchangeRateStored() * (1 + 0.1 * len(n_ccoins)))
            cc.functions.set_exchange_rate(rate).transact(from_alice)
            c.functions.approve(cc.address, n_coins * 10 * u).transact(from_alice)
            cc.functions.mint(n_coins * 10 * u).transact(from_alice)
            n = n_coins * 10 * u * 10 ** 18 // rate
        else:
            n = n_coins * 10 * u
        n_ccoins.append(n)
        if l:
            assert cc.caller.balanceOf(alice) == n
        else:
            assert cc.caller.balanceOf(alice) >= n
        cc.functions.approve(swap.address, n // 10).transact(from_alice)

    # Add some coins
    swap.functions.\
        add_liquidity([n // 10 for n in n_ccoins]).\
        transact(from_alice)

    # Python-based (tested) model with same parameters as contract
    balances = [int(swap.caller.balances(i)) for i in range(3)]
    rates = [int(c.caller.exchangeRateStored()) * p if l else 10 ** 18 * p
             for c, p, l in zip(cerc20s, PRECISIONS, use_lending)]
    curve = Curve(2 * 360, balances, 3, rates)

    for k in range(5):
        for i, j in permutations(range(3), 2):
            dx = random.randrange(2 * n_coins * UU[i])
            rate_x = cerc20s[i].caller.exchangeRateStored() if use_lending[i] else 10 ** 18
            dx_c = dx * 10 ** 18 // rate_x
            dy_1_c = swap.caller.get_dy(i, j, dx_c)
            dy_1_u = swap.caller.get_dy_underlying(i, j, dx)
            dy_2 = curve.dy(i, j, dx * PRECISIONS[i]) // PRECISIONS[j]
            dy_2 = dy_2 * 999 // 1000  # Account for fee
            rate_y = cerc20s[j].caller.exchangeRateStored() if use_lending[j] else 10 ** 18
            dy_1 = dy_1_c * rate_y // 10 ** 18
            assert approx(dy_1, dy_2, 1e-8) or abs(dy_1 - dy_2) <= 2
            assert approx(dy_1_u, dy_2, 1e-8) or abs(dy_1 - dy_2) <= 2
            assert approx(dx_c, swap.caller.get_dx(i, j, dy_1_c), 7e-6)
            assert approx(dx, swap.caller.get_dx_underlying(i, j, dy_1_u), 7e-6)
