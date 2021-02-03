# curve-contract/contracts/pools/yv2

[Curve Aave pool](https://www.curve.fi/yv2), with lending on [Cream](https://v1.yearn.finance/lending).

## Contracts

* [`StableSwapYv2`](StableSwapYv2.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0x571FF5b7b346F706aa48d696a9a4a288e9Bb4091](https://etherscan.io/address/0x571FF5b7b346F706aa48d696a9a4a288e9Bb4091)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0x8101E6760130be2C8Ace79643AB73500571b7162](https://etherscan.io/address/0x8101E6760130be2C8Ace79643AB73500571b7162)
* [`StableSwapYv2`](StableSwapYv2.vy): [0x8925D9d9B4569D737a48499DeF3f67BaA5a144b9](https://etherscan.io/address/0x8925D9d9B4569D737a48499DeF3f67BaA5a144b9)

## Stablecoins

Curve Cream pool supports swaps between the following stablecoins:

### Wrapped

* `cyDAI`: [0x8e595470ed749b85c6f7669de83eae304c2ec68f](https://etherscan.io/address/0x8e595470ed749b85c6f7669de83eae304c2ec68f)
* `aUSDC`: [0x76eb2fe28b36b3ee97f3adae0c69606eedb2a37c](https://etherscan.io/address/0x76eb2fe28b36b3ee97f3adae0c69606eedb2a37c)
* `cyUSDT`: [0x48759f220ed983db51fa7a8c0d2aab8f3ce4166a](https://etherscan.io/address/0x48759f220ed983db51fa7a8c0d2aab8f3ce4166a)

### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
