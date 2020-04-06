from simulation import Curve

A = 900
fee = 4 * 10 ** 6
balances = [506436049869796, 4454102849234208]
rates = [204201050033279995562600854, 210126518129021]
supply = 1029145597899446721562789

xx = [balances[0], balances[1] * 10 ** 12]

curve = Curve(A, xx, 2, rates, tokens=supply)
curve.fee = 0  # fee

# print(curve.dy(0, 1, 10 ** 18) / 1e18)
# print(curve.remove_liquidity_imbalance([10 ** 18 * 10 ** 18 // rates[0], 0]) / 1e18)
# print(curve.remove_liquidity_imbalance([0, 10 ** 18 * 10 ** 18 // rates[1]]) / 1e18)

# print(curve.remove_liquidity_imbalance([0, 48165540 * 10 ** 12  * 10 ** 18 // rates[1]]) / 1e18)
# print(curve.calc_withdraw_one_coin(48056207784846181031, 1) / 1e18)

usdc_amount = curve.calc_withdraw_one_coin(48056207784846181031, 1)
token_amount = curve.remove_liquidity_imbalance([0, usdc_amount  * 10 ** 18 // rates[1]])
print(48056207784846181031, token_amount)
print(usdc_amount)
