import brownie
import pytest

pytestmark = pytest.mark.skip_pool("busd", "compound", "susd", "usdt", "y")

MIN_RAMP_TIME = 86400


def test_ramp_A(chain, alice, swap):
    initial_A = swap.initial_A()
    future_time = chain.time() + MIN_RAMP_TIME+5

    tx = swap.ramp_A(initial_A * 2, future_time, {'from': alice})

    assert swap.initial_A() == initial_A
    assert swap.future_A() == initial_A * 2
    assert swap.initial_A_time() == tx.timestamp
    assert swap.future_A_time() == future_time


def test_ramp_A_final(chain, alice, swap):
    initial_A = swap.initial_A()
    future_time = chain.time() + 1000000

    swap.ramp_A(initial_A * 2, future_time, {'from': alice})

    chain.sleep(1000000)
    chain.mine()

    assert swap.A() == initial_A * 2


def test_ramp_A_value_up(chain, alice, swap):
    initial_A = swap.initial_A()
    future_time = chain.time() + 1000000
    tx = swap.ramp_A(initial_A * 2, future_time, {'from': alice})

    initial_time = tx.timestamp
    duration = future_time - tx.timestamp

    while chain.time() < future_time:
        chain.sleep(100000)
        chain.mine()
        expected = int(initial_A + ((chain.time()-initial_time) / duration) * initial_A)
        assert 0.999 < expected / swap.A() <= 1


def test_ramp_A_value_down(chain, alice, swap):
    initial_A = swap.initial_A()
    future_time = chain.time() + 1000000
    tx = swap.ramp_A(initial_A // 10, future_time, {'from': alice})

    initial_time = tx.timestamp
    duration = future_time - tx.timestamp

    while chain.time() < future_time:
        chain.sleep(100000)
        chain.mine()
        expected = int(initial_A - ((chain.time()-initial_time) / duration) * (initial_A//10*9))
        if expected == 0:
            assert swap.A() == initial_A // 10
        else:
            assert 0.999 < swap.A() / expected <= 1


def test_stop_ramp_A(chain, alice, swap):
    initial_A = swap.initial_A()
    future_time = chain.time() + 1000000
    swap.ramp_A(initial_A * 2, future_time, {'from': alice})

    chain.sleep(31337)

    tx = swap.A.transact({'from': alice})
    current_A = tx.return_value

    swap.stop_ramp_A({'from': alice})

    assert swap.initial_A() == current_A
    assert swap.future_A() == current_A
    assert swap.initial_A_time() == tx.timestamp
    assert swap.future_A_time() == tx.timestamp


def test_ramp_A_only_owner(chain, bob, swap):
    with brownie.reverts():
        swap.ramp_A(0, chain.time()+1000000, {'from': bob})


def test_ramp_A_insufficient_time(chain, alice, swap):
    with brownie.reverts():
        swap.ramp_A(0, chain.time()+MIN_RAMP_TIME-1, {'from': alice})


def test_stop_ramp_A_only_owner(chain, bob, swap):
    with brownie.reverts():
        swap.stop_ramp_A({'from': bob})
