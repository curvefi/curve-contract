# curve-contract/contracts/pools/gusd

[Curve GUSD metapool](https://www.curve.fi/gusd), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`StableSwapGUSD`](StableSwapGUSD.vy): Curve stablecoin AMM contract
* [`DepositGUSD`]

## Deployments

<!--
* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [](https://etherscan.io/address/)
* [`DepositGUSD`](DepositGUSD.vy): [](https://etherscan.io/address/)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [](https://etherscan.io/address/)
* [`StableSwapGUSD`](StableSwapUSDT.vy): [](https://etherscan.io/address/)
 -->

## Stablecoins

Curve GUSD metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between GUSD and the Curve tri-pool LP token.

* `GUSD`: [0x056fd409e1d7a124bd7017459dfea2f387b6d5cd](https://etherscan.io/address/0x056fd409e1d7a124bd7017459dfea2f387b6d5cd)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between GUSD and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
