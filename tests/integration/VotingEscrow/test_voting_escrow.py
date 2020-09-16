from tests.conftest import approx

H = 3600
DAY = 86400
WEEK = 7 * DAY
MAXTIME = 126144000
TOL = 120 / WEEK


def test_voting_powers(web3, chain, accounts,
                       token, voting_escrow):
    """
    Test voting power in the following scenario.
    Alice:
    ~~~~~~~
    ^
    | *       *
    | | \     |  \
    | |  \    |    \
    +-+---+---+------+---> t

    Bob:
    ~~~~~~~
    ^
    |         *
    |         | \
    |         |  \
    +-+---+---+---+--+---> t

    Alice has 100% of voting power in the first period.
    She has 2/3 power at the start of 2nd period, with Bob having 1/2 power
    (due to smaller locktime).
    Alice's power grows to 100% by Bob's unlock.

    Checking that totalSupply is appropriate.

    After the test is done, check all over again with balanceOfAt / totalSupplyAt
    """
    alice, bob = accounts[:2]
    amount = 1000 * 10 ** 18
    token.transfer(bob, amount, {'from': alice})
    stages = {}

    token.approve(voting_escrow.address, amount * 10, {'from': alice})
    token.approve(voting_escrow.address, amount * 10, {'from': bob})

    assert voting_escrow.totalSupply() == 0
    assert voting_escrow.balanceOf(alice) == 0
    assert voting_escrow.balanceOf(bob) == 0

    # Move to timing which is good for testing - beginning of a UTC week
    chain.sleep((chain[-1].timestamp // WEEK + 1) * WEEK - chain[-1].timestamp)
    chain.mine()

    chain.sleep(H)

    stages['before_deposits'] = (web3.eth.blockNumber, chain[-1].timestamp)

    voting_escrow.create_lock(amount, chain[-1].timestamp + WEEK, {'from': alice})
    stages['alice_deposit'] = (web3.eth.blockNumber, chain[-1].timestamp)

    chain.sleep(H)
    chain.mine()

    assert approx(voting_escrow.totalSupply(), amount // MAXTIME * (WEEK - 2 * H), TOL)
    assert approx(voting_escrow.balanceOf(alice), amount // MAXTIME * (WEEK - 2 * H), TOL)
    assert voting_escrow.balanceOf(bob) == 0
    t0 = chain[-1].timestamp

    stages['alice_in_0'] = []
    stages['alice_in_0'].append((web3.eth.blockNumber, chain[-1].timestamp))
    for i in range(7):
        for _ in range(24):
            chain.sleep(H)
            chain.mine()
        dt = chain[-1].timestamp - t0
        assert approx(voting_escrow.totalSupply(), amount // MAXTIME * max(WEEK - 2 * H - dt, 0), TOL)
        assert approx(voting_escrow.balanceOf(alice), amount // MAXTIME * max(WEEK - 2 * H - dt, 0), TOL)
        assert voting_escrow.balanceOf(bob) == 0
        stages['alice_in_0'].append((web3.eth.blockNumber, chain[-1].timestamp))

    chain.sleep(H)

    assert voting_escrow.balanceOf(alice) == 0
    voting_escrow.withdraw({'from': alice})
    stages['alice_withdraw'] = (web3.eth.blockNumber, chain[-1].timestamp)
    assert voting_escrow.totalSupply() == 0
    assert voting_escrow.balanceOf(alice) == 0
    assert voting_escrow.balanceOf(bob) == 0

    chain.sleep(H)
    chain.mine()

    # Next week (for round counting)
    chain.sleep((chain[-1].timestamp // WEEK + 1) * WEEK - chain[-1].timestamp)
    chain.mine()

    voting_escrow.create_lock(amount, chain[-1].timestamp + 2 * WEEK, {'from': alice})
    stages['alice_deposit_2'] = (web3.eth.blockNumber, chain[-1].timestamp)

    assert approx(voting_escrow.totalSupply(), amount // MAXTIME * 2 * WEEK, TOL)
    assert approx(voting_escrow.balanceOf(alice), amount // MAXTIME * 2 * WEEK, TOL)
    assert voting_escrow.balanceOf(bob) == 0

    voting_escrow.create_lock(amount, chain[-1].timestamp + WEEK, {'from': bob})
    stages['bob_deposit_2'] = (web3.eth.blockNumber, chain[-1].timestamp)

    assert approx(voting_escrow.totalSupply(), amount // MAXTIME * 3 * WEEK, TOL)
    assert approx(voting_escrow.balanceOf(alice), amount // MAXTIME * 2 * WEEK, TOL)
    assert approx(voting_escrow.balanceOf(bob), amount // MAXTIME * WEEK, TOL)

    t0 = chain[-1].timestamp
    chain.sleep(H)
    chain.mine()

    stages['alice_bob_in_2'] = []
    # Beginning of week: weight 3
    # End of week: weight 1
    for i in range(7):
        for _ in range(24):
            chain.sleep(H)
            chain.mine()
        dt = chain[-1].timestamp - t0
        w_total = voting_escrow.totalSupply()
        w_alice = voting_escrow.balanceOf(alice)
        w_bob = voting_escrow.balanceOf(bob)
        assert w_total == w_alice + w_bob
        assert approx(w_alice, amount // MAXTIME * max(2 * WEEK - dt, 0), TOL)
        assert approx(w_bob, amount // MAXTIME * max(WEEK - dt, 0), TOL)
        stages['alice_bob_in_2'].append((web3.eth.blockNumber, chain[-1].timestamp))

    chain.sleep(H)
    chain.mine()

    voting_escrow.withdraw({'from': bob})
    t0 = chain[-1].timestamp
    stages['bob_withdraw_1'] = (web3.eth.blockNumber, chain[-1].timestamp)
    w_total = voting_escrow.totalSupply()
    w_alice = voting_escrow.balanceOf(alice)
    assert w_alice == w_total
    assert approx(w_total, amount // MAXTIME * (WEEK - 2 * H), TOL)
    assert voting_escrow.balanceOf(bob) == 0

    chain.sleep(H)
    chain.mine()

    stages['alice_in_2'] = []
    for i in range(7):
        for _ in range(24):
            chain.sleep(H)
            chain.mine()
        dt = chain[-1].timestamp - t0
        w_total = voting_escrow.totalSupply()
        w_alice = voting_escrow.balanceOf(alice)
        assert w_total == w_alice
        assert approx(w_total, amount // MAXTIME * max(WEEK - dt - 2 * H, 0), TOL)
        assert voting_escrow.balanceOf(bob) == 0
        stages['alice_in_2'].append((web3.eth.blockNumber, chain[-1].timestamp))

    voting_escrow.withdraw({'from': alice})
    stages['alice_withdraw_2'] = (web3.eth.blockNumber, chain[-1].timestamp)

    chain.sleep(H)
    chain.mine()

    voting_escrow.withdraw({'from': bob})
    stages['bob_withdraw_2'] = (web3.eth.blockNumber, chain[-1].timestamp)

    assert voting_escrow.totalSupply() == 0
    assert voting_escrow.balanceOf(alice) == 0
    assert voting_escrow.balanceOf(bob) == 0

    # Now test historical balanceOfAt and others

    assert voting_escrow.balanceOfAt(alice, stages['before_deposits'][0]) == 0
    assert voting_escrow.balanceOfAt(bob, stages['before_deposits'][0]) == 0
    assert voting_escrow.totalSupplyAt(stages['before_deposits'][0]) == 0

    w_alice = voting_escrow.balanceOfAt(alice, stages['alice_deposit'][0])
    assert approx(w_alice, amount // MAXTIME * (WEEK - H), TOL)
    assert voting_escrow.balanceOfAt(bob, stages['alice_deposit'][0]) == 0
    w_total = voting_escrow.totalSupplyAt(stages['alice_deposit'][0])
    assert w_alice == w_total

    for i, (block, t) in enumerate(stages['alice_in_0']):
        w_alice = voting_escrow.balanceOfAt(alice, block)
        w_bob = voting_escrow.balanceOfAt(bob, block)
        w_total = voting_escrow.totalSupplyAt(block)
        assert w_bob == 0
        assert w_alice == w_total
        time_left = (WEEK * (7 - i) // 7 - 2 * H)
        error_1h = H / time_left  # Rounding error of 1 block is possible, and we have 1h blocks
        assert approx(w_alice, amount // MAXTIME * time_left, error_1h)

    w_total = voting_escrow.totalSupplyAt(stages['alice_withdraw'][0])
    w_alice = voting_escrow.balanceOfAt(alice, stages['alice_withdraw'][0])
    w_bob = voting_escrow.balanceOfAt(bob, stages['alice_withdraw'][0])
    assert w_alice == w_bob == w_total == 0

    w_total = voting_escrow.totalSupplyAt(stages['alice_deposit_2'][0])
    w_alice = voting_escrow.balanceOfAt(alice, stages['alice_deposit_2'][0])
    w_bob = voting_escrow.balanceOfAt(bob, stages['alice_deposit_2'][0])
    assert approx(w_total, amount // MAXTIME * 2 * WEEK, TOL)
    assert w_total == w_alice
    assert w_bob == 0

    w_total = voting_escrow.totalSupplyAt(stages['bob_deposit_2'][0])
    w_alice = voting_escrow.balanceOfAt(alice, stages['bob_deposit_2'][0])
    w_bob = voting_escrow.balanceOfAt(bob, stages['bob_deposit_2'][0])
    assert w_total == w_alice + w_bob
    assert approx(w_total, amount // MAXTIME * 3 * WEEK, TOL)
    assert approx(w_alice, amount // MAXTIME * 2 * WEEK, TOL)

    t0 = stages['bob_deposit_2'][1]
    for i, (block, t) in enumerate(stages['alice_bob_in_2']):
        w_alice = voting_escrow.balanceOfAt(alice, block)
        w_bob = voting_escrow.balanceOfAt(bob, block)
        w_total = voting_escrow.totalSupplyAt(block)
        assert w_total == w_alice + w_bob
        dt = t - t0
        error_1h = H / (2 * WEEK - i * DAY)  # Rounding error of 1 block is possible, and we have 1h blocks
        assert approx(w_alice, amount // MAXTIME * max(2 * WEEK - dt, 0), error_1h)
        assert approx(w_bob, amount // MAXTIME * max(WEEK - dt, 0), error_1h)

    w_total = voting_escrow.totalSupplyAt(stages['bob_withdraw_1'][0])
    w_alice = voting_escrow.balanceOfAt(alice, stages['bob_withdraw_1'][0])
    w_bob = voting_escrow.balanceOfAt(bob, stages['bob_withdraw_1'][0])
    assert w_total == w_alice
    assert approx(w_total, amount // MAXTIME * (WEEK - 2 * H), TOL)
    assert w_bob == 0

    t0 = stages['bob_withdraw_1'][1]
    for i, (block, t) in enumerate(stages['alice_in_2']):
        w_alice = voting_escrow.balanceOfAt(alice, block)
        w_bob = voting_escrow.balanceOfAt(bob, block)
        w_total = voting_escrow.totalSupplyAt(block)
        assert w_total == w_alice
        assert w_bob == 0
        dt = t - t0
        error_1h = H / (WEEK - i * DAY + DAY)  # Rounding error of 1 block is possible, and we have 1h blocks
        assert approx(w_total, amount // MAXTIME * max(WEEK - dt - 2 * H, 0), error_1h)

    w_total = voting_escrow.totalSupplyAt(stages['bob_withdraw_2'][0])
    w_alice = voting_escrow.balanceOfAt(alice, stages['bob_withdraw_2'][0])
    w_bob = voting_escrow.balanceOfAt(bob, stages['bob_withdraw_2'][0])
    assert w_total == w_alice == w_bob == 0
