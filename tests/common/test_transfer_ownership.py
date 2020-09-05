import brownie

COMMIT_WAIT = 86400 * 3


def test_commit(alice, bob, swap):
    tx = swap.commit_transfer_ownership(bob, {'from': alice})

    assert swap.transfer_ownership_deadline() == tx.timestamp + COMMIT_WAIT
    assert swap.future_owner() == bob


def test_commit_only_owner(bob, swap):
    with brownie.reverts():
        swap.commit_transfer_ownership(bob, {'from': bob})


def test_commit_already_active(alice, bob, swap):
    swap.commit_transfer_ownership(bob, {'from': alice})

    with brownie.reverts():
        swap.commit_transfer_ownership(bob, {'from': alice})


def test_revert(alice, bob, swap):
    swap.commit_transfer_ownership(bob, {'from': alice})
    swap.revert_transfer_ownership({'from': alice})

    assert swap.transfer_ownership_deadline() == 0


def test_revert_only_owner(alice, bob, swap):
    swap.commit_transfer_ownership(bob, {'from': alice})

    with brownie.reverts():
        swap.revert_transfer_ownership({'from': bob})


def test_revert_without_commit(alice, bob, swap):
    swap.revert_transfer_ownership({'from': alice})

    assert swap.transfer_ownership_deadline() == 0


def test_apply(chain, alice, bob, swap):
    swap.commit_transfer_ownership(bob, {'from': alice})
    chain.sleep(COMMIT_WAIT)

    swap.apply_transfer_ownership({'from': alice})

    assert swap.owner() == bob
    assert swap.transfer_ownership_deadline() == 0


def test_apply_only_owner(chain, alice, bob, swap):
    swap.commit_transfer_ownership(bob, {'from': alice})
    chain.sleep(COMMIT_WAIT)

    with brownie.reverts():
        swap.apply_transfer_ownership({'from': bob})


def test_apply_insufficient_time(chain, alice, bob, swap):
    swap.commit_transfer_ownership(bob, {'from': alice})
    chain.sleep(COMMIT_WAIT-5)

    with brownie.reverts():
        swap.apply_transfer_ownership({'from': alice})


def test_apply_no_active_transfer(chain, alice, swap):
    with brownie.reverts():
        swap.apply_transfer_ownership({'from': alice})
