import brownie
import pytest

YEAR = 86400 * 365


@pytest.fixture(scope="module", autouse=True)
def gauge_vote_setup(accounts, chain, gauge_controller, three_gauges, voting_escrow, token):
    gauge_controller.add_type(b'Insurance', {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[0], 0, {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[1], 1, {'from': accounts[0]})

    token.approve(voting_escrow, 10 ** 24, {'from': accounts[0]})
    voting_escrow.create_lock(10 ** 24, chain.time() + YEAR, {'from': accounts[0]})


def test_vote(accounts, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[0], 10000, {'from': accounts[0]})

    assert gauge_controller.vote_user_power(accounts[0]) == 10000


def test_vote_partial(accounts, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[1], 1234, {'from': accounts[0]})

    assert gauge_controller.vote_user_power(accounts[0]) == 1234


def test_vote_change(chain, accounts, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[1], 1234, {'from': accounts[0]})

    with brownie.reverts('Cannot vote so often'):
        gauge_controller.vote_for_gauge_weights(three_gauges[1], 42, {'from': accounts[0]})
    chain.sleep(10 * 86400)
    gauge_controller.vote_for_gauge_weights(three_gauges[1], 42, {'from': accounts[0]})

    assert gauge_controller.vote_user_power(accounts[0]) == 42


def test_vote_remove(chain, accounts, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[1], 10000, {'from': accounts[0]})
    with brownie.reverts('Cannot vote so often'):
        gauge_controller.vote_for_gauge_weights(three_gauges[1], 0, {'from': accounts[0]})
    chain.sleep(10 * 86400)
    gauge_controller.vote_for_gauge_weights(three_gauges[1], 0, {'from': accounts[0]})

    assert gauge_controller.vote_user_power(accounts[0]) == 0


def test_vote_multiple(accounts, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[0], 4000, {'from': accounts[0]})
    gauge_controller.vote_for_gauge_weights(three_gauges[1], 6000, {'from': accounts[0]})

    assert gauge_controller.vote_user_power(accounts[0]) == 10000


def test_vote_no_balance(accounts, gauge_controller, three_gauges):
    with brownie.reverts("Your token lock expires too soon"):
        gauge_controller.vote_for_gauge_weights(three_gauges[0], 10000, {'from': accounts[1]})


def test_vote_expired(accounts, chain, gauge_controller, three_gauges):
    chain.sleep(YEAR * 2)
    with brownie.reverts("Your token lock expires too soon"):
        gauge_controller.vote_for_gauge_weights(three_gauges[0], 10000, {'from': accounts[0]})


def test_invalid_gauge_id(accounts, gauge_controller, three_gauges):
    with brownie.reverts("Gauge not added"):
        gauge_controller.vote_for_gauge_weights(three_gauges[2], 10000, {'from': accounts[0]})


def test_over_user_weight(accounts, gauge_controller, three_gauges):
    with brownie.reverts("You used all your voting power"):
        gauge_controller.vote_for_gauge_weights(three_gauges[0], 10001, {'from': accounts[0]})


def test_over_weight_multiple(accounts, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[0], 8000, {'from': accounts[0]})
    with brownie.reverts('Used too much power'):
        gauge_controller.vote_for_gauge_weights(three_gauges[1], 4000, {'from': accounts[0]})


def test_over_weight_adjust_existing(chain, accounts, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[0], 6000, {'from': accounts[0]})
    gauge_controller.vote_for_gauge_weights(three_gauges[1], 3000, {'from': accounts[0]})

    chain.sleep(10 * 86400)
    with brownie.reverts('Used too much power'):
        gauge_controller.vote_for_gauge_weights(three_gauges[0], 8000, {'from': accounts[0]})
