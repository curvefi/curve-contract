from random import randrange
from .conftest import UU, use_lending, N_COINS


def test_add_liquidity(w3, coins, cerc20s, swap, deposit, pool_token):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}

    def to_compounded(amounts):
        return [
            a * 10 ** 18 // (c.caller.exchangeRateStored() if l else 10 ** 18)
            for a, c, l in zip(amounts, cerc20s, use_lending)]

    def add_and_test(amounts):
        for c, a in zip(coins, amounts):
            c.functions.approve(deposit.address, a).transact(from_sam)
        c_amounts = to_compounded(amounts)
        if swap.caller.balances(0) > 0:
            min_amount = swap.caller.calc_token_amount(c_amounts, True)
        else:
            min_amount = 0

        balances_before = [swap.caller.balances(i) for i in range(N_COINS)]
        token_before = pool_token.caller.balanceOf(sam)
        deposit.functions.add_liquidity(
            amounts, int(0.999 * min_amount)
        ).transact(from_sam)
        token_after = pool_token.caller.balanceOf(sam)
        balances_after = [swap.caller.balances(i) for i in range(N_COINS)]

        for i in range(N_COINS):
            assert balances_after[i] - balances_before[i] == c_amounts[i]

        assert token_after - token_before > 0
        assert token_after - token_before >= int(0.999 * min_amount)

    # Add random amounts many times
    for i in range(5):
        amounts = [randrange(1000 * u) + 1 for u in UU]
        add_and_test(amounts)

        coin = randrange(N_COINS)
        amounts = [0] * N_COINS
        amounts[coin] = randrange(1000 * UU[coin]) + 1
        add_and_test(amounts)
