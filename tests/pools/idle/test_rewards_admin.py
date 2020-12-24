
import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(swap, alice, bob, charlie):
    swap.set_reward_claimant(bob, {'from': alice})
    swap.set_reward_admin(charlie, {'from': alice})


def test_assumptions(swap, bob, charlie):
    assert swap.reward_claimant() == bob
    assert swap.reward_admin() == charlie


def test_set_reward_claimant(alice, charlie, swap):
    swap.set_reward_claimant(charlie, {'from': alice})
    assert swap.reward_claimant() == charlie


def test_set_reward_admin(alice, bob, swap):
    swap.set_reward_admin(bob, {'from': alice})
    assert swap.reward_admin() == bob


@pytest.mark.parametrize('idx', range(1, 5))
def test_set_reward_claimant_only_owner(accounts, swap, idx):
    with brownie.reverts("dev: only owner"):
        swap.set_reward_claimant(accounts[0], {'from': accounts[idx]})


@pytest.mark.parametrize('idx', range(1, 5))
def test_set_reward_admin_only_owner(accounts, swap, idx):
    with brownie.reverts("dev: only owner"):
        swap.set_reward_admin(accounts[0], {'from': accounts[idx]})
