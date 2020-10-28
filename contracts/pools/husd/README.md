# curve-contract/contracts/pools/husd

[Curve HUSD metapool](https://www.curve.fi/husd), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositHUSD`](DepositHUSD.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapHUSD`](StableSwapHUSD.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0x5B5CFE992AdAC0C9D48E05854B2d91C73a003858](https://etherscan.io/address/0x5B5CFE992AdAC0C9D48E05854B2d91C73a003858)
* [`DepositHUSD`](DepositHUSD.vy): [0x09672362833d8f703D5395ef3252D4Bfa51c15ca](https://etherscan.io/address/0x09672362833d8f703D5395ef3252D4Bfa51c15ca)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [0x2db0E83599a91b508Ac268a6197b8B14F5e72840](https://etherscan.io/address/0x2db0E83599a91b508Ac268a6197b8B14F5e72840)
* [`StableSwapHUSD`](StableSwapHUSD.vy): [0x3eF6A01A0f81D6046290f3e2A8c5b843e738E604](https://etherscan.io/address/0x3eF6A01A0f81D6046290f3e2A8c5b843e738E604)

## Stablecoins

Curve HUSD metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between HUSD and the Curve tri-pool LP token.

* `HUSD`: [0xdf574c24545e5ffecb9a659c229253d4111d87e1](https://etherscan.io/address/0xdf574c24545e5ffecb9a659c229253d4111d87e1)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between HUSD and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
