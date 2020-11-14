import brownie
import pytest

COMMIT_WAIT = 86400 * 3
MAX_ADMIN_FEE = 5 * 10 ** 9
MAX_FEE = 5 * 10 ** 9

pytestmark = pytest.mark.skip_pool("aave", "busd", "compound", "susd", "usdt", "y")


@pytest.mark.parametrize(
    "fee,admin_fee", [
        (0, 0),
        (23, 42),
        (MAX_FEE, MAX_ADMIN_FEE),
        (1, MAX_ADMIN_FEE),
    ]
)
def test_commit(alice, swap, fee, admin_fee):
    tx = swap.commit_new_fee(fee, admin_fee, {'from': alice})

    assert swap.admin_actions_deadline() == tx.timestamp + COMMIT_WAIT
    assert swap.future_fee() == fee
    assert swap.future_admin_fee() == admin_fee


def test_commit_only_owner(bob, swap):
    with brownie.reverts():
        swap.commit_new_fee(23, 42, {'from': bob})


def test_commit_already_active(alice, swap):
    swap.commit_new_fee(23, 42, {'from': alice})
    with brownie.reverts():
        swap.commit_new_fee(23, 42, {'from': alice})


@pytest.mark.parametrize("fee", [2**127, 2**256-1])
def test_commit_admin_fee_too_high(alice, swap, fee):
    with brownie.reverts():
        swap.commit_new_fee(0, fee, {'from': alice})


@pytest.mark.parametrize("fee", [MAX_FEE+1, 2**127, 2**256-1])
def test_commit_fee_too_high(alice, swap, fee):
    with brownie.reverts():
        swap.commit_new_fee(fee, 0, {'from': alice})


@pytest.mark.parametrize(
    "fee,admin_fee", [
        (0, 0),
        (23, 42),
        (MAX_FEE, MAX_ADMIN_FEE),
        (1, MAX_ADMIN_FEE),
    ]
)
def test_apply(chain, alice, swap, fee, admin_fee):
    swap.commit_new_fee(fee, admin_fee, {'from': alice})
    chain.sleep(COMMIT_WAIT)
    swap.apply_new_fee({'from': alice})

    assert swap.admin_actions_deadline() == 0
    assert swap.fee() == fee
    assert swap.admin_fee() == admin_fee


def test_apply_only_owner(chain, alice, bob, swap):
    swap.commit_new_fee(0, 0, {'from': alice})
    chain.sleep(COMMIT_WAIT)

    with brownie.reverts():
        swap.apply_new_fee({'from': bob})


@pytest.mark.parametrize('time', [0, COMMIT_WAIT-2])
def test_apply_insufficient_time(chain, alice, swap, time):
    swap.commit_new_fee(0, 0, {'from': alice})
    chain.sleep(time)
    with brownie.reverts():
        swap.apply_new_fee({'from': alice})


def test_apply_no_action(alice, swap):
    with brownie.reverts():
        swap.apply_new_fee({'from': alice})


def test_revert(alice, swap):
    swap.commit_new_fee(0, 0, {'from': alice})
    swap.revert_new_parameters({'from': alice})

    assert swap.admin_actions_deadline() == 0


def test_revert_only_owner(alice, bob, swap):
    swap.commit_new_fee(0, 0, {'from': alice})
    with brownie.reverts():
        swap.revert_new_parameters({'from': bob})


def test_revert_without_commit(alice, swap):
    swap.revert_new_parameters({'from': alice})

    assert swap.admin_actions_deadline() == 0


def test_withdraw_only_owner(bob, swap):
    with brownie.reverts():
        swap.withdraw_admin_fees({'from': bob})
