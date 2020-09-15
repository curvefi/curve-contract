"""
Tests to verify that a pool integrates with the registry contract.
https://github.com/curvefi/curve-pool-registry
"""

import pytest

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


@pytest.fixture(scope="module", autouse=True)
def setup(alice, underlying_coins, wrapped_coins, swap, initial_amounts):
    # mint (10**6 * precision) of each coin in the pool
    for underlying, wrapped, amount in zip(underlying_coins, wrapped_coins, initial_amounts):
        underlying._mint_for_testing(alice, amount, {'from': alice})
        underlying.approve(wrapped, 2**256-1, {'from': alice})
        wrapped.approve(swap, 2**256-1, {'from': alice})
        if hasattr(wrapped, "mint"):
            wrapped.mint(amount, {'from': alice})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})


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


@pytest.mark.lending
@pytest.mark.itercoins("send", "recv")
def test_exchange(alice, registry, wrapped_coins, swap, send, recv):
    send_token = wrapped_coins[send]
    recv_token = wrapped_coins[recv]

    send_token._mint_for_testing(alice, 10**18, {'from': alice})
    send_token.approve(registry, 10**18, {'from': alice})
    expected = registry.get_exchange_amount(swap, send_token, recv_token, 10**18)

    registry.exchange(swap, send_token, recv_token, 10**18, 0, {'from': alice})
    assert send_token.balanceOf(alice) == 0
    assert recv_token.balanceOf(alice) / expected == pytest.approx(1)


@pytest.mark.lending
@pytest.mark.itercoins("send", "recv")
def test_exchange_underlying(alice, registry, underlying_coins, swap, send, recv):
    send_token = underlying_coins[send]
    recv_token = underlying_coins[recv]

    send_token._mint_for_testing(alice, 10**18, {'from': alice})
    send_token.approve(registry, 10**18, {'from': alice})
    expected = registry.get_exchange_amount(swap, send_token, recv_token, 10**18)

    registry.exchange(swap, send_token, recv_token, 10**18, 0, {'from': alice})
    assert send_token.balanceOf(alice) == 0
    assert recv_token.balanceOf(alice) / expected == pytest.approx(1)
