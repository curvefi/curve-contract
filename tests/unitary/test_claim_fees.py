import itertools

import brownie
import pytest

from tests.conftest import PRECISIONS

INITIAL_AMOUNTS = [10**(i+6) for i in PRECISIONS]
MAX_FEE = 5 * 10**9


@pytest.fixture(scope="module", autouse=True)
def setup(chain, alice, bob, coins, swap):
    for coin, amount in zip(coins[:-1], INITIAL_AMOUNTS[:-1]):
        for acct in (alice, bob):
            coin._mint_for_testing(acct, amount, {'from': acct})
            coin.approve(swap, 2**256-1, {'from': acct})

    # Give Bob 1 million of metacoins
    coins[-1].transfer(bob, INITIAL_AMOUNTS[-1], {'from': alice})
    # Leave Alice 1 million of metacoins
    coins[-1].transfer(
            coins[-1], coins[-1].balanceOf(alice) - INITIAL_AMOUNTS[-1],
            {'from': alice})
    coins[-1].approve(swap, 2**256-1, {'from': alice})
    coins[-1].approve(swap, 2**256-1, {'from': bob})

    swap.add_liquidity(INITIAL_AMOUNTS, 0, {'from': alice})

    swap.commit_new_fee(MAX_FEE, MAX_FEE, {'from': alice})
    chain.sleep(86400*3)
    swap.apply_new_fee({'from': alice})


def test_admin_balances(alice, bob, swap, coins):
    for send, recv in [(0, 1), (1, 0)]:
        swap.exchange(send, recv, INITIAL_AMOUNTS[send], 0, {'from': bob})

    for i in range(2):
        admin_fee = swap.admin_balances(i)
        assert admin_fee > 0
        assert admin_fee + swap.balances(i) == coins[i].balanceOf(swap)


@pytest.mark.parametrize("sending,receiving", itertools.permutations([0, 1], 2))
def test_withdraw_one_coin(alice, bob, swap, coins, sending, receiving):
    swap.exchange(sending, receiving, INITIAL_AMOUNTS[sending], 0, {'from': bob})

    admin_fee = swap.admin_balances(receiving)
    assert admin_fee > 0

    assert swap.admin_balances(sending) == 0

    swap.withdraw_admin_fees({'from': alice})
    assert coins[receiving].balanceOf(alice) == admin_fee
    assert swap.admin_balances(receiving) == 0


def test_withdraw_all_coins(alice, bob, swap, coins):
    for send, recv in [(0, 1), (1, 0)]:
        swap.exchange(send, recv, INITIAL_AMOUNTS[send], 0, {'from': bob})

    admin_fees = [swap.admin_balances(i) for i in range(2)]

    swap.withdraw_admin_fees({'from': alice})
    balances = [i.balanceOf(alice) for i in coins]

    assert admin_fees == balances


def test_withdraw_only_owner(bob, swap):
    with brownie.reverts("dev: only owner"):
        swap.withdraw_admin_fees({'from': bob})


def test_donate(alice, bob, swap, coins):
    for send, recv in [(0, 1), (1, 0)]:
        swap.exchange(send, recv, INITIAL_AMOUNTS[send], 0, {'from': bob})

    swap.donate_admin_fees({'from': alice})

    assert [swap.admin_balances(i) for i in range(2)] == [0, 0]
    assert [i.balanceOf(alice) for i in coins] == [0, 0]


def test_donate_only_owner(bob, swap):
    with brownie.reverts("dev: only owner"):
        swap.withdraw_admin_fees({'from': bob})
