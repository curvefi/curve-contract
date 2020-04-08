import pytest
from eth_tester.exceptions import TransactionFailed
from random import randrange, random
from .conftest import UU, N_COINS, approx


def test_add_remove_liquidity(w3, coins, yerc20s, swap, deposit, pool_token):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}
    rates = [c.caller.getPricePerFullShare() for c in yerc20s]

    def to_compounded(amounts):
        return [a * 10 ** 18 // r for a, r in zip(amounts, rates)]

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
        amounts = [randrange(u, 1000 * u) + 1 for u in UU]
        add_and_test(amounts)

        coin = randrange(N_COINS)
        amounts = [0] * N_COINS
        amounts[coin] = randrange(UU[coin], 1000 * UU[coin]) + 1
        add_and_test(amounts)

    # Remove liquidity
    token_before = pool_token.caller.balanceOf(sam)
    ubalances = [swap.caller.balances(i) * r // 10 ** 18 for i, r in enumerate(rates)]
    sam_balances = [c.caller.balanceOf(sam) for c in coins]
    pool_token.functions.approve(deposit.address, token_before).transact(from_sam)
    with pytest.raises(TransactionFailed):
        deposit.functions.remove_liquidity(
                token_before // 10, [int(0.11 * u) for u in ubalances]
                ).transact(from_sam)
    deposit.functions.remove_liquidity(
            token_before // 10, [int(0.0999 * u) for u in ubalances]
            ).transact(from_sam)
    token_after = pool_token.caller.balanceOf(sam)
    ubalances_after = [swap.caller.balances(i) * r // 10 ** 18 for i, r in enumerate(rates)]
    assert approx(token_after / token_before, 0.9, 1e-7)
    for c, u1, u0, oldbal in zip(coins, ubalances_after, ubalances, sam_balances):
        assert approx(u1 / u0, 0.9, 1e-7)
        assert abs((c.caller.balanceOf(sam) - oldbal) - (u0 - u1)) <= 1

    # Remove liquidity imbalance
    to_withdraw = [u0 - u1 for u0, u1 in zip(ubalances, ubalances_after)]
    # to_withdraw is 1/9 of what is left
    expected_dtoken = token_before - token_after
    token_before = token_after
    ubalances = ubalances_after
    with pytest.raises(TransactionFailed):
        deposit.functions.remove_liquidity_imbalance(
                to_withdraw, int(0.999 * expected_dtoken)).transact(from_sam)
    deposit.functions.remove_liquidity_imbalance(
            to_withdraw, int(1.01 * expected_dtoken)).transact(from_sam)
    token_after = pool_token.caller.balanceOf(sam)
    ubalances_after = [swap.caller.balances(i) * r // 10 ** 18 for i, r in enumerate(rates)]
    assert approx(token_after / token_before, 8 / 9, 1e-7)
    assert pool_token.caller.balanceOf(deposit.address) == 0
    for c, u1, u0, oldbal in zip(coins, ubalances_after, ubalances, sam_balances):
        assert approx(u1 / u0, 8 / 9, 1e-7)
        assert abs((c.caller.balanceOf(sam) - oldbal) // 2 - (u0 - u1)) <= 1


def test_withdraw_one_coin(w3, coins, yerc20s, swap, deposit, pool_token):
    for _run in range(25):
        print(_run)

        sam = w3.eth.accounts[0]  # Sam owns the bank
        from_sam = {'from': sam}
        amounts = [randrange(100000 * u, 1000000 * u) for u in UU]

        # First, deposit, measure amounts and withdraw everything
        for c, a in zip(coins, amounts):
            c.functions.approve(deposit.address, a).transact(from_sam)
        deposit.functions.add_liquidity(amounts, 0).transact(from_sam)

        ii = randrange(N_COINS)
        amount = randrange(1, int(0.9 * amounts[ii])) if random() < 0.5\
            else randrange(1, min(1000 * UU[ii], amounts[ii] // 2))
        amounts_to_remove = [0] * N_COINS
        amounts_to_remove[ii] = amount

        token_before = pool_token.caller.balanceOf(sam)

        pool_token.functions.approve(deposit.address, token_before).transact(from_sam)
        deposit.functions.remove_liquidity_imbalance(
                amounts_to_remove, token_before
                ).transact(from_sam)
        token_after = pool_token.caller.balanceOf(sam)
        dtoken = token_before - token_after

        pool_token.functions.approve(deposit.address, token_after).transact(from_sam)
        deposit.functions.remove_liquidity(token_after, [0] * N_COINS).transact(from_sam)

        # Now withdraw just one coin
        # Deposit exactly the same amounts
        for c, a in zip(coins, amounts):
            c.functions.approve(deposit.address, a).transact(from_sam)
        deposit.functions.add_liquidity(amounts, 0).transact(from_sam)
        token_before = pool_token.caller.balanceOf(sam)
        pool_token.functions.approve(deposit.address, token_before).transact(from_sam)

        calc_amount = deposit.caller.calc_withdraw_one_coin(dtoken, ii)
        print(amount, calc_amount)

        amount_before = coins[ii].caller.balanceOf(sam)
        with pytest.raises(TransactionFailed):
            deposit.functions.remove_liquidity_one_coin(dtoken, ii, int(1.001 * calc_amount)).transact(from_sam)
        if random() < 0.5:
            donate_dust = []
        else:
            donate_dust = [True]
        deposit.functions.remove_liquidity_one_coin(dtoken, ii, int(0.999 * calc_amount), *donate_dust).transact(from_sam)
        amount_after = coins[ii].caller.balanceOf(sam)
        token_after = pool_token.caller.balanceOf(sam)

        assert approx(amount_after - amount_before, amount, 2.5e-4)
        assert token_before - token_after <= dtoken
        assert approx(token_before - token_after, dtoken, 2.5e-4)

        # Withdraw all back
        deposit.functions.withdraw_donated_dust().transact({'from': w3.eth.accounts[1]})
        pool_token.functions.transfer(
            sam,
            pool_token.caller.balanceOf(w3.eth.accounts[1])).transact({'from': w3.eth.accounts[1]})
        pool_token.functions.approve(deposit.address, 0).transact(from_sam)
        to_remove = pool_token.caller.balanceOf(sam)
        pool_token.functions.approve(deposit.address, to_remove).transact(from_sam)
        deposit.functions.remove_liquidity(to_remove, [0] * N_COINS).transact(from_sam)

        # Reset approvals
        for c in coins:
            c.functions.approve(deposit.address, 0).transact(from_sam)
        pool_token.functions.approve(deposit.address, 0).transact(from_sam)
