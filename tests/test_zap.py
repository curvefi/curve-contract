import pytest
from random import randrange
from eth_tester.exceptions import TransactionFailed
from .conftest import UU, UUY


@pytest.mark.parametrize("amounts", [[randrange(1000, 30000) for i in range(5)] for j in range(4)])
def test_deposit_withdraw(w3, ypool, coins, coins_y, yerc20s, yerc20s_y, pool_token_y, swap2, deposit, amounts):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}

    coins = [coins[0]] + coins_y
    ycoins = [yerc20s[0]] + yerc20s_y

    U = [UU[0]] + UUY
    amounts = [u * a for u, a in zip(U, amounts)]
    rates = [c.caller.getPricePerFullShare() for c in ycoins]
    camounts = [a * 10 ** 18 // r for a, r in zip(amounts, rates)]
    half_amounts = [a // 2 for a in amounts]

    # Deposit plain
    for amount, c in zip(amounts, coins):
        c.functions.approve(deposit.address, amount).transact(from_sam)
    # For the first deposit, calc_token_amount is not working
    deposit.functions.add_liquidity(half_amounts, 0).transact(from_sam)
    # The second one should though
    token_amount = deposit.caller.calc_token_amount(camounts, True)
    with pytest.raises(TransactionFailed):
        deposit.functions.add_liquidity(half_amounts, int(1.01 * token_amount / 2)).transact(from_sam)
    deposit.functions.add_liquidity(half_amounts, int(0.99 * token_amount / 2)).transact(from_sam)

    # Test that we have amounts deposited
    assert abs(swap2.caller.balances(0) - camounts[0]) <= 1
    for i in range(1, 5):
        assert abs(ypool.caller.balances(i - 1) - camounts[i]) <= 1
