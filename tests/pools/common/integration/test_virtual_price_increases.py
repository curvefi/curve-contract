import pytest
from brownie.test import given, strategy
from hypothesis import settings

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_bob")


@given(
    st_coin=strategy('decimal[100]', min_value=0, max_value="0.99", unique=True, places=2),
    st_divisor=strategy('uint[50]', min_value=1, max_value=100, unique=True),
)
@settings(max_examples=5)
def test_number_go_up(
    chain,
    bob,
    wrapped_coins,
    wrapped_decimals,
    swap,
    n_coins,
    st_coin,
    st_divisor,
    set_fees,
):
    """
    Perform a series of token swaps and compare the resulting amounts and pool balances
    with those in our python-based model.

    Strategies
    ----------
    st_coin : decimal[100]
        Array of decimal values, used to choose the coins used in each swap
    st_divisor: uint[50]
        Array of integers, used to choose the size of each swap
    """

    set_fees(10**7, 0)

    rate_mul = [10**i for i in wrapped_decimals]
    while st_coin:
        # Tune exchange rates
        for coin in wrapped_coins:
            if hasattr(coin, 'set_exchange_rate'):
                rate = int(coin.get_rate() * 1.0001)
                coin.set_exchange_rate(rate, {'from': bob})

        old_virtual_price = swap.get_virtual_price()

        chain.sleep(60)

        # choose which coins to swap
        send, recv = [int(st_coin.pop() * n_coins) for _ in range(2)]
        if send == recv:
            # if send and recv are the same, adjust send
            send = abs(send - 1)

        value = 5 * rate_mul[send] // st_divisor.pop()

        min_amount = int(0.5 * value * rate_mul[recv] / rate_mul[send])
        swap.exchange(send, recv, value, min_amount, {'from': bob})

        assert swap.get_virtual_price() >= old_virtual_price
