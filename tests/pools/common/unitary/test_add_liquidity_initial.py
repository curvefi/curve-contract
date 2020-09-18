import brownie
import pytest

pytestmark = pytest.mark.usefixtures("mint_alice", "approve_alice")

ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


@pytest.mark.parametrize("min_amount", [0, 2 * 10**18])
def test_initial(
    alice, swap, wrapped_coins, pool_token, min_amount, wrapped_decimals, n_coins, initial_amounts
):
    amounts = [10**i for i in wrapped_decimals]
    value = "1 ether" if ETH_ADDRESS in wrapped_coins else 0

    swap.add_liquidity(amounts, min_amount, {'from': alice, 'value': value})

    for coin, amount, initial in zip(wrapped_coins, amounts, initial_amounts):
        if coin == ETH_ADDRESS:
            assert alice.balance() + amount == initial
            assert swap.balance() == amount
        else:
            assert coin.balanceOf(alice) == initial - amount
            assert coin.balanceOf(swap) == amount

    assert pool_token.balanceOf(alice) == n_coins * 10**18
    assert pool_token.totalSupply() == n_coins * 10**18


@pytest.mark.itercoins("idx")
def test_initial_liquidity_missing_coin(alice, swap, pool_token, idx, wrapped_decimals):
    amounts = [10**i for i in wrapped_decimals]
    amounts[idx] = 0

    with brownie.reverts():
        swap.add_liquidity(amounts, 0, {'from': alice})
