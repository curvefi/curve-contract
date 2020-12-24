import brownie
import pytest
from brownie import ZERO_ADDRESS


@pytest.fixture(scope="module", autouse=True)
def setup(swap, alice, bob):
    swap.set_reward_admin(bob, {'from': alice})


def test_assumptions(swap, alice, bob):
    assert swap.owner() == alice
    assert swap.reward_admin() == bob
    assert [swap.reward_tokens(i) for i in range(8)] == [ZERO_ADDRESS] * 8


def test_set_rewards_one(swap, alice, charlie):
    swap.set_rewards([charlie] + [ZERO_ADDRESS] * 7, {'from': alice})

    assert [swap.reward_tokens(i) for i in range(8)] == [charlie] + [ZERO_ADDRESS] * 7


def test_set_reward_some(swap, alice, bob, charlie):
    swap.set_rewards([charlie, alice, bob] + [ZERO_ADDRESS] * 5, {'from': alice})

    assert [swap.reward_tokens(i) for i in range(8)] == [charlie, alice, bob] + [ZERO_ADDRESS] * 5


def test_set_rewards_full(swap, alice, accounts):
    swap.set_rewards(accounts[:8], {'from': alice})

    assert [swap.reward_tokens(i) for i in range(8)] == accounts[:8]


def test_set_rewards_none(swap, alice, accounts):
    swap.set_rewards(accounts[:8], {'from': alice})
    swap.set_rewards([ZERO_ADDRESS] * 8, {'from': alice})

    assert [swap.reward_tokens(i) for i in range(8)] == [ZERO_ADDRESS] * 8


def test_set_reward_increase_length(swap, alice, bob, charlie):
    swap.set_rewards([charlie] + [ZERO_ADDRESS] * 7, {'from': alice})
    swap.set_rewards([alice, bob, charlie] + [ZERO_ADDRESS] * 5, {'from': alice})

    assert [swap.reward_tokens(i) for i in range(8)] == [alice, bob, charlie] + [ZERO_ADDRESS] * 5


def test_set_reward_decrease_length(swap, alice, bob, charlie):
    swap.set_rewards([charlie, alice, bob] + [ZERO_ADDRESS] * 5, {'from': alice})

    swap.set_rewards([alice, charlie] + [ZERO_ADDRESS] * 6, {'from': alice})

    assert [swap.reward_tokens(i) for i in range(8)] == [alice, charlie] + [ZERO_ADDRESS] * 6


def test_reward_admin_can_set(swap, bob):
    swap.set_rewards([ZERO_ADDRESS] * 8, {'from': bob})


@pytest.mark.itercoins('idx')
def test_cannot_set_pool_coins(swap, alice, idx):
    with brownie.reverts("dev: pool coin"):
        swap.set_rewards([swap.coins(idx)] + [ZERO_ADDRESS] * 7, {'from': alice})


@pytest.mark.parametrize('idx', range(2, 5))
def test_only_owner(swap, accounts, idx):
    with brownie.reverts("dev: only owner"):
        swap.set_rewards([ZERO_ADDRESS] * 8, {'from': accounts[idx]})
