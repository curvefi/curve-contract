# curve-contract/contracts/pools/susd

[Curve sUSD pool](https://www.curve.fi/susdv2). This is a no-lending pool.

## Contracts

* [`DepositSUSD`](DepositSUSD.vy): Depositor contract. Used to handle withdrawal of a single coin.
* [`StableSwapSUSD`](StableSwapSUSD.vy): Curve stablecoin AMM contract.

## Deployments

* [`CurveContractV1`](../../tokens/CurveTokenV1.vy): [0xC25a3A3b969415c80451098fa907EC722572917F](https://etherscan.io/address/0xC25a3A3b969415c80451098fa907EC722572917F)
* [`DepositSUSD`](DepositSUSD.vy): [0xfcba3e75865d2d561be8d220616520c171f12851](https://etherscan.io/address/0xfcba3e75865d2d561be8d220616520c171f12851)
* [`LiquidityGaugeReward`](../../gauges/LiquidityGaugeReward.vy): [0xA90996896660DEcC6E997655E065b23788857849](https://etherscan.io/address/0xa90996896660decc6e997655e065b23788857849)
* [`StableSwapSUSD`](StableSwapSUSD.vy): [0xA5407eAE9Ba41422680e2e00537571bcC53efBfD](https://etherscan.io/address/0xA5407eAE9Ba41422680e2e00537571bcC53efBfD)

## Stablecoins

Curve sUSD pool supports swaps between the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
* `sUSD`: [0x57ab1ec28d129707052df4df418d58a2d46d5f51](https://etherscan.io/address/0x57ab1ec28d129707052df4df418d58a2d46d5f51)
