import pytest

YEAR = 86400 * 365


@pytest.fixture(scope="module", autouse=True)
def gauge_vote_setup(accounts, chain, gauge_controller, three_gauges, voting_escrow, token):
    gauge_controller.add_type(b'Insurance', {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[0], 0, {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[1], 1, {'from': accounts[0]})

    token.approve(voting_escrow, 10 ** 24, {'from': accounts[0]})
    voting_escrow.create_lock(10 ** 24, chain.time() + YEAR, {'from': accounts[0]})


def test_no_immediate_effect_on_weight(accounts, chain, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[0], 10000, {'from': accounts[0]})
    assert not gauge_controller.gauge_relative_weight(three_gauges[0])


def test_effect_on_following_period(accounts, chain, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[0], 10000, {'from': accounts[0]})

    chain.sleep(86400 * 7)
    gauge_controller.checkpoint_gauge(three_gauges[0], {'from': accounts[0]})
    assert gauge_controller.gauge_relative_weight(three_gauges[0]) == 10**18  # 1.0 * 1e18


def test_remove_vote_no_immediate_effect(accounts, chain, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[0], 10000, {'from': accounts[0]})
    chain.sleep(86400 * 10)

    gauge_controller.checkpoint_gauge(three_gauges[0], {'from': accounts[0]})
    gauge_controller.vote_for_gauge_weights(three_gauges[0], 0, {'from': accounts[0]})

    assert gauge_controller.gauge_relative_weight(three_gauges[0]) == 10**18


def test_remove_vote_means_no_weight(accounts, chain, gauge_controller, three_gauges):
    gauge_controller.vote_for_gauge_weights(three_gauges[0], 10000, {'from': accounts[0]})
    chain.sleep(86400 * 10)
    gauge_controller.checkpoint_gauge(three_gauges[0], {'from': accounts[0]})

    assert gauge_controller.gauge_relative_weight(three_gauges[0]) == 10 ** 18

    gauge_controller.vote_for_gauge_weights(three_gauges[0], 0, {'from': accounts[0]})

    chain.sleep(86400 * 7)
    gauge_controller.checkpoint_gauge(three_gauges[0], {'from': accounts[0]})

    assert not gauge_controller.gauge_relative_weight(three_gauges[0])
