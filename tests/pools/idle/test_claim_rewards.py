import pytest
from brownie import ZERO_ADDRESS


pytestmark = pytest.mark.usefixtures("add_initial_liquidity")


@pytest.fixture(scope="module")
def gauge(LiquidityGaugeV2Mock, alice, pool_token, swap, reward_a, reward_b):
    contract = LiquidityGaugeV2Mock.deploy(pool_token, {'from': alice})
    pool_token.approve(contract, 2**256-1, {'from': alice})
    contract.deposit(pool_token.balanceOf(alice), {'from': alice})

    reward_tokens = [reward_a, reward_b] + [ZERO_ADDRESS] * 6
    sigs = f"0x{'00'*4}{'00'*4}{contract.claim_rewards[()].signature[2:]}{'00'*20}"

    swap.set_reward_claimant(contract, {'from': alice})
    swap.set_rewards(reward_tokens, {'from': alice})
    contract.set_rewards(swap, sigs, reward_tokens, {'from': alice})

    yield contract


@pytest.fixture(scope="module")
def reward_a(ERC20Mock, alice):
    yield ERC20Mock.deploy("Reward A", "A", 18, {'from': alice})


@pytest.fixture(scope="module")
def reward_b(ERC20Mock, alice):
    yield ERC20Mock.deploy("Reward B", "B", 18, {'from': alice})


def test_claim(alice, swap, gauge, reward_a, reward_b):
    reward_a._mint_for_testing(swap, 10**18, {'from': alice})
    reward_b._mint_for_testing(swap, 10**19, {'from': alice})
    gauge.claim_rewards({'from': alice})

    assert 0.9999 < reward_a.balanceOf(alice) / 10**18 < 1
    assert 0.9999 < reward_b.balanceOf(alice) / 10**19 < 1
