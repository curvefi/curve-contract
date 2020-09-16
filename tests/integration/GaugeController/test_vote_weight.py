import pytest

from hypothesis import settings

from brownie import history, chain
from brownie.test import given, strategy

WEEK = 86400 * 7
YEAR = 86400 * 365


@pytest.fixture(scope="module", autouse=True)
def setup(gauge_controller, accounts, three_gauges, token, voting_escrow):
    # We handle setup logic in a fixture to avoid repeating it in each test run

    # Set up gauges and types
    gauge_controller.add_type(b'Liquidity', 10**18, {'from': accounts[0]})
    for gauge in three_gauges:
        gauge_controller.add_gauge(gauge, 0, {'from': accounts[0]})

    # Distribute coins
    for acct in accounts[:3]:
        token.transfer(acct, 10 ** 24, {'from': accounts[0]})
        token.approve(voting_escrow, 10 ** 24, {'from': acct})


@given(
    st_deposits=strategy('uint256[3]', min_value=10**21, max_value=10**23),
    st_length=strategy('uint256[3]', min_value=52, max_value=100),
    st_votes=strategy('uint[2][3]', min_value=0, max_value=5)
)
@settings(max_examples=10)
def test_gauge_weight_vote(
    accounts, gauge_controller, three_gauges, voting_escrow, st_deposits, st_length, st_votes
):
    """
    Test that gauge weights correctly adjust over time.

    Strategies
    ---------
    st_deposits : [int, int, int]
        Number of coins to be deposited per account
    st_length : [int, int, int]
        Policy duration in weeks
    st_votes : [(int, int), (int, int), (int, int)]
        (vote for gauge 0, vote for gauge 1) for each account, in units of 10%
    """

    # Init 10 s before the week change
    t0 = chain.time()
    t1 = (t0 + 2 * WEEK) // WEEK * WEEK - 10
    chain.sleep(t1 - t0)

    # Deposit for voting
    timestamp = t1
    for i, acct in enumerate(accounts[:3]):
        voting_escrow.create_lock(st_deposits[i], timestamp + (st_length[i] * WEEK), {'from': acct})

    # Place votes
    votes = []
    for i, acct in enumerate(accounts[:3]):
        votes.append([x*1000 for x in st_votes[i]])
        votes[-1].append(10000 - sum(votes[-1]))  # XXX what if votes are not used up to 100%?
        # Now votes are [[vote_gauge_0, vote_gauge_1, vote_gauge_2], ...]
        for x in range(3):
            gauge_controller.vote_for_gauge_weights(three_gauges[x], votes[-1][x], {'from': acct})

    # Vote power assertions - everyone used all voting power
    for acct in accounts[:3]:
        assert gauge_controller.vote_user_power(acct) == 10000

    # Calculate slope data, build model functions
    slope_data = []
    for i, acct in enumerate(accounts[:3]):
        initial_bias = voting_escrow.get_last_user_slope(acct) * (voting_escrow.locked(acct)[1] - timestamp)
        duration = (timestamp + st_length[i] * WEEK) // WEEK * WEEK - timestamp  # <- endtime rounded to whole weeks
        slope_data.append((initial_bias, duration))

    max_duration = max(duration for bias, duration in slope_data)

    def models(idx, relative_time):
        bias, duration = slope_data[idx]
        return max(bias * (1 - relative_time * max_duration / duration), 0)

    chain.sleep(WEEK * 4)
    chain.mine()

    # advance clock a month at a time and compare theoretical weight to actual weights
    while history[-1].timestamp < timestamp + 1.5 * max_duration:
        for i in range(3):
            gauge_controller.checkpoint_gauge(three_gauges[i], {'from': accounts[4]})

        relative_time = (history[-1].timestamp // WEEK * WEEK - timestamp) / max_duration
        weights = [gauge_controller.gauge_relative_weight(three_gauges[i]) / 1e18 for i in range(3)]

        if relative_time < 1:
            theoretical_weights = [
                sum((votes[i][0]/10000) * models(i, relative_time) for i in range(3)),
                sum((votes[i][1]/10000) * models(i, relative_time) for i in range(3)),
                sum((votes[i][2]/10000) * models(i, relative_time) for i in range(3)),
            ]
            theoretical_weights = [w and (w / sum(theoretical_weights)) for w in theoretical_weights]
        else:
            theoretical_weights = [0] * 3

        print(relative_time, weights, theoretical_weights)
        if relative_time != 1:  # XXX 1 is odd: let's look at it separately
            for i in range(3):
                assert abs(weights[i] - theoretical_weights[i]) <= (history[-1].timestamp - timestamp) / WEEK + 1  # 1 s per week?

        chain.sleep(WEEK * 4)
        chain.mine()
