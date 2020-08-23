import itertools

import pytest

from tests.conftest import PRECISIONS

INITIAL_AMOUNTS = [10**(i+6) for i in PRECISIONS]


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, coins, swap):
    for coin, amount in zip(coins, INITIAL_AMOUNTS):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': bob})

    swap.add_liquidity(INITIAL_AMOUNTS, 0, {'from': alice})


@pytest.mark.parametrize("sending,receiving", itertools.permutations([0, 1], 2))
@pytest.mark.parametrize(
    "fee,admin_fee", itertools.combinations_with_replacement([0, 0.04, 0.1337, 0.5], 2)
)
def test_exchange(chain, alice, bob, swap, coins, sending, receiving, fee, admin_fee):
    if fee or admin_fee:
        swap.commit_new_fee(int(10**10 * fee), int(10**10 * admin_fee), {'from': alice})
        chain.sleep(86400*3)
        swap.apply_new_fee({'from': alice})

    amount = 10**PRECISIONS[sending]
    coins[sending]._mint_for_testing(bob, amount, {'from': bob})
    swap.exchange(sending, receiving, amount, 0, {'from': bob})

    assert coins[sending].balanceOf(bob) == 0

    received = coins[receiving].balanceOf(bob)
    assert 0.9999-fee < received / 10**PRECISIONS[receiving] < 1-fee

    expected_admin_fee = 10**PRECISIONS[receiving] * fee * admin_fee
    if expected_admin_fee:
        assert (expected_admin_fee * 0.999) <= swap.admin_balances(receiving) <= expected_admin_fee
    else:
        assert swap.admin_balances(receiving) == 0


@pytest.mark.parametrize("sending,receiving", itertools.permutations([0, 1], 2))
def test_min_dy(bob, swap, coins, sending, receiving):
    amount = 10**PRECISIONS[sending]
    coins[sending]._mint_for_testing(bob, amount, {'from': bob})

    min_dy = swap.get_dy(sending, receiving, amount)
    swap.exchange(sending, receiving, amount, min_dy, {'from': bob})

    assert coins[receiving].balanceOf(bob) == min_dy
