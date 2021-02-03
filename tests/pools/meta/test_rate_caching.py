import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity")


def test_virtual_price(chain, bob, swap, initial_amounts, n_coins):
    virtual_price = swap.get_virtual_price()

    chain.sleep(86400)
    chain.mine()

    assert virtual_price == swap.get_virtual_price()


@pytest.mark.itercoins("sending", "receiving")
def test_get_dy(chain, swap, sending, receiving, wrapped_decimals):
    amount = 10 ** wrapped_decimals[sending]
    min_dy = swap.get_dy(sending, receiving, amount)

    chain.sleep(86400)
    chain.mine()

    assert min_dy == swap.get_dy(sending, receiving, amount)


@pytest.mark.lending
@pytest.mark.itercoins("sending", "receiving", underlying=True)
def test_get_dy_underlying(chain, swap, sending, receiving, underlying_decimals):
    amount = 10 ** underlying_decimals[sending]
    min_dy = swap.get_dy_underlying(sending, receiving, amount)

    chain.sleep(86400)
    chain.mine()

    assert min_dy == swap.get_dy_underlying(sending, receiving, amount)


@pytest.mark.itercoins("idx")
def test_calc_withdraw_one_coin(chain, alice, swap, pool_token, idx):
    amount = pool_token.balanceOf(alice)
    expected = swap.calc_withdraw_one_coin(amount, idx)

    chain.sleep(86400)
    chain.mine()

    assert expected == swap.calc_withdraw_one_coin(amount, idx)


@pytest.mark.parametrize("is_deposit", [True, False])
def test_calc_token_amount(chain, swap, wrapped_decimals, is_deposit):
    amounts = [10 ** i for i in wrapped_decimals]
    expected = swap.calc_token_amount(amounts, is_deposit)

    chain.sleep(86400)
    chain.mine()

    assert expected == swap.calc_token_amount(amounts, is_deposit)
