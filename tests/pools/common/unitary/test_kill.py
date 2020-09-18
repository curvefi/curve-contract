import brownie
import pytest


def test_kill(alice, swap):
    swap.kill_me({'from': alice})


def test_kill_approaching_deadline(chain, alice, swap):
    chain.sleep(59 * 86400)
    swap.kill_me({'from': alice})


def test_kill_only_owner(bob, swap):
    with brownie.reverts():
        swap.kill_me({'from': bob})


def test_kill_beyond_deadline(chain, alice, swap):
    chain.sleep(60 * 86400)
    with brownie.reverts():
        swap.kill_me({'from': alice})


def test_kill_and_unkill(alice, swap):
    swap.kill_me({'from': alice})
    swap.unkill_me({'from': alice})


def test_unkill_without_kill(alice, swap):
    swap.unkill_me({'from': alice})


def test_unkill_only_owner(bob, swap):
    with brownie.reverts():
        swap.unkill_me({'from': bob})


def test_remove_liquidity(
    add_initial_liquidity, alice, swap, wrapped_coins, initial_amounts, n_coins, base_amount
):
    swap.kill_me({'from': alice})
    swap.remove_liquidity(n_coins * 10**18 * base_amount, [0] * n_coins, {'from': alice})


def test_remove_liquidity_imbalance(alice, swap, initial_amounts, n_coins):
    swap.kill_me({'from': alice})

    with brownie.reverts():
        swap.remove_liquidity_imbalance([0] * n_coins, 0, {'from': alice})


@pytest.mark.skip_pool("busd", "compound", "pax", "susd", "usdt", "y")
def test_remove_liquidity_one_coin(alice, swap):
    swap.kill_me({'from': alice})

    with brownie.reverts():
        swap.remove_liquidity_one_coin(0, 0, 0, {'from': alice})


def test_exchange(alice, swap):
    swap.kill_me({'from': alice})

    with brownie.reverts():
        swap.exchange(0, 0, 0, 0, {'from': alice})
