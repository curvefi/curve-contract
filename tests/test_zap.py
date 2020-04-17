import pytest
from random import randrange


@pytest.mark.parametrize("amounts", [[randrange(1000, 30000) for i in range(5)] for j in range(4)])
def test_deposit_withdraw(w3, ypool, coins, coins_y, yerc20s, yerc20s_y, pool_token_y, swap2, deposit, amounts):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}

    coins = [coins[0]] + coins_y
    ycoins = [yerc20s[0]] + yerc20s_y

    rates = [c.caller.getPricePerFullShare() for c in ycoins]
    camounts = [a * 10 ** 18 // r for a, r in zip(amounts, rates)]
    half_amounts = [a // 2 for a in amounts]

    # Deposit plain
    for amount, c in zip(amounts, coins):
        c.functions.approve(deposit.address, amount).transact(from_sam)
    # For the first deposit, calc_token_amount is not working
    deposit.functions.add_liquidity(half_amounts, 0).transact(from_sam)
    return  # XXX
    # The second one should though
    token_amount = deposit.caller.calc_token_amount(camounts, True)
    deposit.functions.add_liquidity(half_amounts, int(1.01 * token_amount)).transact(from_sam)
