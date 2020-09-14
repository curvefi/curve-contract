import itertools

import pytest

from tests.conftest import PRECISIONS, BASE_PRECISIONS

INITIAL_AMOUNTS = [10**(i+6) for i in PRECISIONS]


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, bank, coins, swap):
    for coin, amount in zip(coins[:-1], INITIAL_AMOUNTS[:-1]):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': bob})
        coin._mint_for_testing(bank, amount, {'from': bank})

    # Leave Alice 1 million of metacoins
    coins[-1].transfer(
            bank, coins[-1].balanceOf(alice) - INITIAL_AMOUNTS[-1],
            {'from': alice})
    coins[-1].approve(swap, 2**256-1, {'from': alice})
    coins[-1].approve(swap, 2**256-1, {'from': bob})

    swap.add_liquidity(INITIAL_AMOUNTS, 0, {'from': alice})


@pytest.mark.parametrize("sending,receiving", itertools.permutations(range(4), 2))
@pytest.mark.parametrize(
    "fee,admin_fee", itertools.combinations_with_replacement([0, 0.04, 0.1337, 0.5], 2)
)
@pytest.mark.parametrize("base_volume", [0, 10**7])
def test_exchange_underlying(chain, alice, bob, bank, swap, coins, sending, receiving, fee, admin_fee,
                             base_swap, base_coins, base_volume):
    underlying_coins = coins[:-1] + base_coins
    underlying_precisions = PRECISIONS[:-1] + BASE_PRECISIONS
    base_fee = base_swap.fee() / 1e10

    if base_volume:
        base_coins[0]._mint_for_testing(alice, base_volume * 10**BASE_PRECISIONS[0], {'from': alice})
        base_swap.exchange(0, 1, base_volume * 10**BASE_PRECISIONS[0], 0, {'from': alice})
        dump_amount = base_coins[1].balanceOf(alice)
        base_swap.exchange(1, 0, dump_amount, 0, {'from': alice})
        chain.sleep(3600)  # Making sure that the metapool will update virtual price

    if fee or admin_fee:
        swap.commit_new_fee(int(10**10 * fee), int(10**10 * admin_fee), {'from': alice})
        chain.sleep(86400*3)
        swap.apply_new_fee({'from': alice})

    amount = 10**underlying_precisions[sending]
    underlying_coins[sending].transfer(bob, amount, {'from': bank})
    swap.exchange_underlying(sending, receiving, amount, 0, {'from': bob})

    assert underlying_coins[sending].balanceOf(bob) == 0

    received = underlying_coins[receiving].balanceOf(bob)
    assert (0.9999 - fee - base_fee/2) < received / 10**underlying_precisions[receiving] < (1.0001-fee-base_fee/2)

    # XXX fees are not in underlying
    expected_admin_fee = 10**underlying_precisions[receiving] * fee * admin_fee

    if expected_admin_fee:
        assert (expected_admin_fee * 0.998) <= swap.admin_balances(receiving) <= (1.02 * expected_admin_fee)
    else:
        assert swap.admin_balances(receiving) == 0


@pytest.mark.parametrize("sending,receiving", itertools.permutations(range(4), 2))
def test_min_dy(bob, bank, swap, coins, sending, receiving):
    amount = 10**PRECISIONS[sending]
    coins[sending].transfer(bob, amount, {'from': bank})

    min_dy = swap.get_dy(sending, receiving, amount)
    swap.exchange(sending, receiving, amount, min_dy, {'from': bob})

    assert coins[receiving].balanceOf(bob) == min_dy
