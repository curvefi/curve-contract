
import brownie

from tests.conftest import approx


def to_int(*args):
    # Helper function for readability
    return [int(a) for a in args]


def test_mint(accounts, chain, mock_lp_token, gauge_controller, three_gauges, minter, token):
    admin, bob, charlie, dan = accounts[:4]

    token.set_minter(minter, {'from': admin})

    W = 10 ** 18
    amount = 10 ** 18
    type_weights = to_int(0.5 * W, 2 * W)
    gauge_weights = to_int(2 * W, 1 * W, 0.5 * W)
    gauge_types = [0, 0, 1]

    # Set up types
    for i, w in enumerate(type_weights):
        gauge_controller.add_type(b'Liquidity', {'from': admin})
        gauge_controller.change_type_weight(i, w, {'from': admin})

    # Set up gauges
    for g, t, w in zip(three_gauges, gauge_types, gauge_weights):
        gauge_controller.add_gauge(g, t, w, {'from': admin})

    # Transfer tokens to Bob, Charlie and Dan
    for user in accounts[1:4]:
        mock_lp_token.transfer(user, amount, {'from': admin})

    chain.sleep(7 * 86400)  # For weights to activate

    # Bob and Charlie deposit to gauges with different weights
    mock_lp_token.approve(three_gauges[1], amount, {'from': bob})
    three_gauges[1].deposit(amount, {'from': bob})
    mock_lp_token.approve(three_gauges[2], amount, {'from': charlie})
    three_gauges[2].deposit(amount, {'from': charlie})

    dt = 30 * 86400
    chain.sleep(dt)
    chain.mine()

    mock_lp_token.approve(three_gauges[1], amount, {'from': dan})
    three_gauges[1].deposit(amount, {'from': dan})

    chain.sleep(dt)
    chain.mine()

    with brownie.reverts():
        # Cannot withdraw too much
        three_gauges[1].withdraw(amount + 1, {'from': bob})

    # Withdraw
    three_gauges[1].withdraw(amount, {'from': bob})
    three_gauges[2].withdraw(amount, {'from': charlie})
    three_gauges[1].withdraw(amount, {'from': dan})

    for user in accounts[1:4]:
        assert mock_lp_token.balanceOf(user) == amount

    # Claim for Bob now
    minter.mint(three_gauges[1], {'from': bob})
    bob_tokens = token.balanceOf(bob)

    chain.sleep(dt)
    chain.mine()

    minter.mint(three_gauges[1], {'from': bob})  # This won't give anything
    assert bob_tokens == token.balanceOf(bob)

    minter.mint(three_gauges[2], {'from': charlie})
    charlie_tokens = token.balanceOf(charlie)
    minter.mint(three_gauges[1], {'from': dan})
    dan_tokens = token.balanceOf(dan)

    S = bob_tokens + charlie_tokens + dan_tokens
    ww = [w * type_weights[t] for w, t in zip(gauge_weights, gauge_types)]
    Sw = ww[1] + ww[2]  # Gauge 0 not used

    # Bob and Charlie were there for full time, gauges 1 and 2
    # Dan was in gauge 1 for half the time
    assert approx(bob_tokens / S, 0.75 * ww[1] / Sw, 2e-6)
    assert approx(charlie_tokens / S, ww[2] / Sw, 2e-6)
    assert approx(dan_tokens / S, 0.25 * ww[1] / Sw, 2e-6)
