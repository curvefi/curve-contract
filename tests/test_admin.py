import pytest
from time import time
from eth_tester.exceptions import TransactionFailed


def test_transfer_ownership(tester, w3, swap):
    alice, bob, charlie = w3.eth.accounts[:3]

    # Only admin can withdraw fees
    # even if there are no fees, the call will fail for non-admin
    # Initially, the owner is Bob
    swap.functions.withdraw_admin_fees().transact({'from': bob})
    with pytest.raises(TransactionFailed):
        swap.functions.withdraw_admin_fees().transact({'from': alice})

    # Only allowed party can transfer ownership
    with pytest.raises(TransactionFailed):
        swap.functions.commit_transfer_ownership(alice).transact({'from': charlie})

    # Bob is allowed to do it
    swap.functions.commit_transfer_ownership(alice).transact({'from': bob})

    # However, Bob still cannot apply it
    with pytest.raises(TransactionFailed):
        swap.functions.apply_transfer_ownership().transact({'from': bob})

    # Travel a bit more than 7 days in future
    tester.time_travel(int(time()) + 86400 * 7 + 2000)
    tester.mine_block()

    # And now the ownership transfer should work
    swap.functions.apply_transfer_ownership().transact({'from': bob})

    # Test that transfer indeed occurred
    swap.functions.withdraw_admin_fees().transact({'from': alice})
    with pytest.raises(TransactionFailed):
        swap.functions.withdraw_admin_fees().transact({'from': bob})

    # Now test reverting it
    swap.functions.commit_transfer_ownership(charlie).transact({'from': alice})
    swap.functions.revert_transfer_ownership().transact({'from': alice})

    tester.time_travel(int(time()) + (86400 * 7 + 2000) * 2)
    tester.mine_block()

    # Cannot transfer after reverting
    with pytest.raises(TransactionFailed):
        swap.functions.apply_transfer_ownership().transact({'from': alice})
