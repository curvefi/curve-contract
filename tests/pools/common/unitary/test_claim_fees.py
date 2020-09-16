import brownie
import pytest


MAX_FEE = 5 * 10**9


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, wrapped_coins, swap, initial_amounts, set_fees):
    for coin, amount in zip(wrapped_coins, initial_amounts):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin._mint_for_testing(bob, amount, {'from': bob})
        coin.approve(swap, 2**256-1, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': bob})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})
    set_fees(MAX_FEE, MAX_FEE)


@pytest.mark.itercoins("sending", "receiving")
def test_admin_balances(alice, bob, swap, wrapped_coins, initial_amounts, sending, receiving):
    for send, recv in [(sending, receiving), (receiving, sending)]:
        swap.exchange(send, recv, initial_amounts[send], 0, {'from': bob})

    for i in (sending, receiving):
        admin_fee = wrapped_coins[i].balanceOf(swap) - swap.balances(i)
        assert admin_fee > 0
        assert admin_fee + swap.balances(i) == wrapped_coins[i].balanceOf(swap)


@pytest.mark.itercoins("sending", "receiving")
def test_withdraw_one_coin(
    alice, bob, swap, wrapped_coins, sending, receiving, initial_amounts, get_admin_balances
):

    swap.exchange(sending, receiving, initial_amounts[sending], 0, {'from': bob})

    admin_balances = get_admin_balances()

    assert admin_balances[receiving] > 0
    assert sum(admin_balances) == admin_balances[receiving]

    swap.withdraw_admin_fees({'from': alice})
    assert wrapped_coins[receiving].balanceOf(alice) == admin_balances[receiving]

    assert swap.balances(receiving) == wrapped_coins[receiving].balanceOf(swap)


def test_withdraw_all_coins(alice, bob, swap, wrapped_coins, initial_amounts, get_admin_balances):
    for send, recv in [(0, 1), (1, 0)]:
        swap.exchange(send, recv, initial_amounts[send], 0, {'from': bob})

    admin_balances = get_admin_balances()

    swap.withdraw_admin_fees({'from': alice})
    balances = [i.balanceOf(alice) for i in wrapped_coins]

    assert admin_balances == balances


def test_withdraw_only_owner(bob, swap):
    with brownie.reverts():
        swap.withdraw_admin_fees({'from': bob})
