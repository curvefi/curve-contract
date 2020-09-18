import brownie
import pytest

MAX_FEE = 5 * 10**9
ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


@pytest.fixture(scope="module", autouse=True)
def setup(alice, add_initial_liquidity, mint_bob, approve_bob, set_fees):
    set_fees(MAX_FEE, MAX_FEE)


@pytest.mark.itercoins("sending", "receiving")
def test_admin_balances(alice, bob, swap, wrapped_coins, initial_amounts, sending, receiving):
    for send, recv in [(sending, receiving), (receiving, sending)]:
        value = initial_amounts[send] if wrapped_coins[send] == ETH_ADDRESS else 0
        swap.exchange(send, recv, initial_amounts[send], 0, {'from': bob, 'value': value})

    for i in (sending, receiving):
        if wrapped_coins[i] == ETH_ADDRESS:
            admin_fee = swap.balance() - swap.balances(i)
            assert admin_fee + swap.balances(i) == swap.balance()
        else:
            admin_fee = wrapped_coins[i].balanceOf(swap) - swap.balances(i)
            assert admin_fee + swap.balances(i) == wrapped_coins[i].balanceOf(swap)

        assert admin_fee > 0


@pytest.mark.itercoins("sending", "receiving")
def test_withdraw_one_coin(
    alice, bob, swap, wrapped_coins, sending, receiving, initial_amounts, get_admin_balances
):

    value = 0
    if wrapped_coins[sending] == ETH_ADDRESS:
        value = initial_amounts[sending]

    swap.exchange(sending, receiving, initial_amounts[sending], 0, {'from': bob, 'value': value})

    admin_balances = get_admin_balances()

    assert admin_balances[receiving] > 0
    assert sum(admin_balances) == admin_balances[receiving]

    swap.withdraw_admin_fees({'from': alice})

    if wrapped_coins[receiving] == ETH_ADDRESS:
        assert alice.balance() == admin_balances[receiving]
        assert swap.balances(receiving) == swap.balance()
    else:
        assert wrapped_coins[receiving].balanceOf(alice) == admin_balances[receiving]
        assert swap.balances(receiving) == wrapped_coins[receiving].balanceOf(swap)


def test_withdraw_all_coins(
    alice, bob, swap, wrapped_coins, initial_amounts, get_admin_balances, n_coins
):
    for send, recv in zip(range(n_coins), list(range(1, n_coins)) + [0]):
        value = initial_amounts[send] if wrapped_coins[send] == ETH_ADDRESS else 0
        swap.exchange(send, recv, initial_amounts[send], 0, {'from': bob, 'value': value})

    admin_balances = get_admin_balances()

    swap.withdraw_admin_fees({'from': alice})

    for balance, coin in zip(admin_balances, wrapped_coins):
        if coin == ETH_ADDRESS:
            assert balance == alice.balance()
        else:
            assert coin.balanceOf(alice) == balance


def test_withdraw_only_owner(bob, swap):
    with brownie.reverts():
        swap.withdraw_admin_fees({'from': bob})
