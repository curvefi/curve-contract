import pytest
from random import randrange, random
from eth_tester.exceptions import TransactionFailed
from .conftest import UU, UUY, approx


@pytest.mark.parametrize("amounts", [[randrange(1000, 30000) for i in range(5)] for j in range(4)])
def test_deposit_withdraw(
        w3, ypool, coins, coins_y, yerc20s, yerc20s_y, pool_token_y, swap2,
        pool_token, deposit, amounts):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}

    coins = [coins[0]] + coins_y
    ycoins = [yerc20s[0]] + yerc20s_y

    U = [UU[0]] + UUY
    amounts = [u * a for u, a in zip(U, amounts)]
    rates = [c.caller.getPricePerFullShare() for c in ycoins]
    camounts = [a * 10 ** 18 // r for a, r in zip(amounts, rates)]
    half_amounts = [a // 2 for a in amounts]

    old_balances = [c.caller.balanceOf(sam) for c in coins]

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

    tokens = pool_token.caller.balanceOf(sam)
    balances = [c.caller.balanceOf(sam) for c in coins]

    for old, new, a in zip(old_balances, balances, amounts):
        assert abs((old - new) - a) <= 1

    # Accrue 0-100% interest
    for i in range(len(ycoins)):
        mult = 1 + random()
        r = int(rates[i] * mult)
        ycoins[i].functions.set_exchange_rate(r).transact(from_sam)
        half_amounts[i] = half_amounts[i] * r // rates[i]
        rates[i] = r
    # Coins in these tests are pretty much goxcoins, so we won't have 100% available

    # Let's withdraw half of everything
    old_balances = balances[:]
    pool_token.functions.approve(deposit.address, tokens // 2).transact(from_sam)
    with pytest.raises(TransactionFailed):
        deposit.functions.remove_liquidity(tokens // 2, [int(1.01 * a) for a in half_amounts]).transact(from_sam)
    deposit.functions.remove_liquidity(tokens // 2, [int(0.99 * a) for a in half_amounts]).transact(from_sam)
    balances = [c.caller.balanceOf(sam) for c in coins]
    for old, new, a in zip(old_balances, balances, half_amounts):
        assert approx((new - old), a, 1e-8)  # <- approx b/c of precision of rates


def test_remove_liquidity_imbalance(
        w3, ypool, coins, coins_y, yerc20s, yerc20s_y, pool_token_y, swap2,
        pool_token, deposit):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}

    coins = [coins[0]] + coins_y
    ycoins = [yerc20s[0]] + yerc20s_y

    U = [UU[0]] + UUY
    amounts = [10000 * u for u in U]
    rates = [c.caller.getPricePerFullShare() for c in ycoins]

    # Deposit plain
    for amount, c in zip(amounts, coins):
        c.functions.approve(deposit.address, amount).transact(from_sam)
    # For the first deposit, calc_token_amount is not working
    deposit.functions.add_liquidity(amounts, 0).transact(from_sam)

    old_balances = [c.caller.balanceOf(sam) for c in coins]

    # Remove imbalance
    withdraw_amounts = [int(a * random() / 2) for a in amounts]
    camounts = [a * 10 ** 18 // r for a, r in zip(withdraw_amounts, rates)]
    token_amount = deposit.caller.calc_token_amount(camounts, False)
    token_amount = int(1.002 * token_amount)
    pool_token.functions.approve(deposit.address, token_amount).transact(from_sam)
    with pytest.raises(TransactionFailed):
        deposit.functions.remove_liquidity_imbalance(withdraw_amounts, int(0.99 * token_amount)).transact(from_sam)
    deposit.functions.remove_liquidity_imbalance(withdraw_amounts, token_amount).transact(from_sam)

    balances = [c.caller.balanceOf(sam) for c in coins]

    for old, new, a in zip(old_balances, balances, withdraw_amounts):
        assert approx((new - old), a, 1e-10)


@pytest.mark.parametrize("i", range(5))
def test_withdraw_one_coin(
        w3, ypool, coins, coins_y, yerc20s, yerc20s_y, pool_token_y, swap2,
        pool_token, deposit, i):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}

    coins = [coins[0]] + coins_y
    ycoins = [yerc20s[0]] + yerc20s_y

    U = [UU[0]] + UUY
    amounts = [10000 * u for u in U]
    rates = [c.caller.getPricePerFullShare() for c in ycoins]

    # Deposit plain
    for amount, c in zip(amounts, coins):
        c.functions.approve(deposit.address, amount).transact(from_sam)
    # For the first deposit, calc_token_amount is not working
    deposit.functions.add_liquidity(amounts, 0).transact(from_sam)

    tokens = pool_token.caller.balanceOf(sam)
    old_balances = [c.caller.balanceOf(sam) for c in coins]

    tokens_to_withdraw = int(0.1 * random() * tokens)
    coins_to_withdraw = deposit.caller.calc_withdraw_one_coin(tokens_to_withdraw, i)

    # Double-check that back-calculation approximately works
    _amounts = [0] * len(U)
    _amounts[i] = coins_to_withdraw * 10 ** 18 // rates[i]
    tokens_recheck = deposit.caller.calc_token_amount(_amounts, False)
    assert approx(tokens_to_withdraw, tokens_recheck, 0.002)  # 2 x fee

    # Withdraw one coin
    pool_token.functions.approve(deposit.address, tokens_to_withdraw).transact(from_sam)
    # Don't donate dust
    deposit.functions.remove_liquidity_one_coin(
            tokens_to_withdraw // 2, i, int(0.5 * 0.999 * coins_to_withdraw)
    ).transact(from_sam)
    # Donate dust
    deposit.functions.remove_liquidity_one_coin(
            tokens_to_withdraw - tokens_to_withdraw // 2, i, int(0.5 * 0.999 * coins_to_withdraw), True
    ).transact(from_sam)

    balances = [c.caller.balanceOf(sam) for c in coins]

    for j in range(len(U)):
        if j == i:
            assert approx(balances[j] - old_balances[j], coins_to_withdraw, 2e-4)
        else:
            assert balances[j] == old_balances[j]
