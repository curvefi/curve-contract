

def test_initial_assumptions(alice, swap):
    assert swap.get_coin_rates() == [10**18] * 6


def test_modify_wrapped_price(alice, swap, wrapped_coins):
    rates = [10**18 * i for i in range(5)] + [10**18]
    for rate, coin in zip(rates, wrapped_coins[:-1]):
        coin.set_exchange_rate(rate)

    assert swap.get_coin_rates() == rates


def test_modify_ycrv_virtual_price(alice, swap, swap_mock):
    rates = [10**18] * 6
    rates[4] = int(1.337e18)

    swap_mock._set_virtual_price(rates[4])

    assert swap.get_coin_rates() == rates


def test_modify_wrapped_and_ycrv(alice, swap, wrapped_coins, swap_mock):
    rates = [10**18 * i for i in range(5)] + [10**18]
    for rate, coin in zip(rates, wrapped_coins[:-1]):
        coin.set_exchange_rate(rate)

    swap_mock._set_virtual_price(int(1.337e18))
    rates[4] = rates[4] * int(1.337e18) // 1e18

    assert swap.get_coin_rates() == rates
