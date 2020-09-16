
from brownie.test import given, strategy
import pytest

WEEK = 86400 * 7


@pytest.fixture(scope="module", autouse=True)
def setup(accounts, token, voting_escrow):
    token.approve(voting_escrow, 10**18, {'from': accounts[0]})


@given(
    st_initial=strategy('uint', min_value=WEEK*2, max_value=WEEK*52),
    st_extend=strategy('uint', min_value=WEEK, max_value=WEEK*2),
)
def test_create_lock_zero_balance(accounts, chain, token, voting_escrow, st_initial, st_extend):
    expected_unlock = chain.time() + st_initial
    voting_escrow.create_lock(10**18, expected_unlock, {'from': accounts[0]})

    actual_unlock = voting_escrow.locked(accounts[0])[1]

    chain.sleep(actual_unlock - chain.time() - 5)
    chain.mine()
    assert voting_escrow.balanceOf(accounts[0])

    chain.sleep(10)
    chain.mine()
    assert not voting_escrow.balanceOf(accounts[0])


@given(
    st_initial=strategy('uint', min_value=WEEK*2, max_value=WEEK*52),
    st_extend=strategy('uint', min_value=WEEK, max_value=WEEK*2),
)
def test_increase_unlock_zero_balance(accounts, chain, token, voting_escrow, st_initial, st_extend):
    voting_escrow.create_lock(10**18, chain.time() + st_initial, {'from': accounts[0]})

    initial_unlock = voting_escrow.locked(accounts[0])[1]
    extended_expected_unlock = initial_unlock + st_extend

    voting_escrow.increase_unlock_time(extended_expected_unlock)
    extended_actual_unlock = voting_escrow.locked(accounts[0])[1]

    chain.sleep(extended_actual_unlock - chain.time() - 5)
    chain.mine()
    assert voting_escrow.balanceOf(accounts[0])

    chain.sleep(10)
    chain.mine()
    assert not voting_escrow.balanceOf(accounts[0])
