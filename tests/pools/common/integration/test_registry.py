"""
Tests to verify that a pool integrates with the registry contract.
https://github.com/curvefi/curve-pool-registry
"""

import pytest

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

pytestmark = pytest.mark.usefixtures("add_initial_liquidity")


@pytest.mark.itercoins("send", "recv")
def test_amount_dy(registry, swap, send, recv):
    dy = swap.get_dy(send, recv, 10**18)
    send_address = swap.coins(send)
    recv_address = swap.coins(recv)
    assert registry.get_exchange_amount(swap, send_address, recv_address, 10**18) == dy


@pytest.mark.lending
@pytest.mark.itercoins("send", "recv")
def test_amount_dy_underlying(registry, swap, send, recv):
    dy = swap.get_dy_underlying(send, recv, 10**18)
    send_address = swap.underlying_coins(send)
    recv_address = swap.underlying_coins(recv)
    assert registry.get_exchange_amount(swap, send_address, recv_address, 10**18) == dy


@pytest.mark.itercoins("send", "recv")
def test_exchange(bob, registry, wrapped_coins, wrapped_decimals, swap, send, recv):
    send_token = wrapped_coins[send]
    recv_token = wrapped_coins[recv]

    amount = 10**wrapped_decimals[send]
    send_token._mint_for_testing(bob, amount, {'from': bob})
    send_token.approve(registry, amount, {'from': bob})
    expected = registry.get_exchange_amount(swap, send_token, recv_token, amount)

    registry.exchange(swap, send_token, recv_token, amount, 0, {'from': bob})
    assert send_token.balanceOf(bob) == 0
    assert recv_token.balanceOf(bob) / expected == pytest.approx(1)


@pytest.mark.lending
@pytest.mark.itercoins("send", "recv")
def test_exchange_underlying(bob, registry, underlying_coins, underlying_decimals, swap, send, recv):
    send_token = underlying_coins[send]
    recv_token = underlying_coins[recv]

    amount = 10**underlying_decimals[send]
    send_token._mint_for_testing(bob, amount, {'from': bob})
    send_token.approve(registry, amount, {'from': bob})
    expected = registry.get_exchange_amount(swap, send_token, recv_token, amount)

    registry.exchange(swap, send_token, recv_token, amount, 0, {'from': bob})
    assert send_token.balanceOf(bob) == 0
    assert recv_token.balanceOf(bob) / expected == pytest.approx(1)
