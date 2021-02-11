# curve-contract/contracts/pools/ib

[Curve Iron Bank pool](https://www.curve.fi/ib), with lending on [Cream](https://v1.yearn.finance/lending).

## Contracts

* [`StableSwapIB`](StableSwapIB.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0x5282a4eF67D9C33135340fB3289cc1711c13638C](https://etherscan.io/address/0x5282a4eF67D9C33135340fB3289cc1711c13638C)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0xF5194c3325202F456c95c1Cf0cA36f8475C1949F](https://etherscan.io/address/0xF5194c3325202F456c95c1Cf0cA36f8475C1949F)
* [`StableSwapIB`](StableSwapIB.vy): [0x2dded6Da1BF5DBdF597C45fcFaa3194e53EcfeAF](https://etherscan.io/address/0x2dded6Da1BF5DBdF597C45fcFaa3194e53EcfeAF)

## Stablecoins

Curve Iron Bank pool supports swaps between the following stablecoins:

### Wrapped

* `cyDAI`: [0x8e595470ed749b85c6f7669de83eae304c2ec68f](https://etherscan.io/address/0x8e595470ed749b85c6f7669de83eae304c2ec68f)
* `aUSDC`: [0x76eb2fe28b36b3ee97f3adae0c69606eedb2a37c](https://etherscan.io/address/0x76eb2fe28b36b3ee97f3adae0c69606eedb2a37c)
* `cyUSDT`: [0x48759f220ed983db51fa7a8c0d2aab8f3ce4166a](https://etherscan.io/address/0x48759f220ed983db51fa7a8c0d2aab8f3ce4166a)

### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
