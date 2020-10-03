# curve-contract/contracts/pools/usdn

[Curve USDN metapool](https://www.curve.fi/usdn), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`StableSwapUSDN`](StableSwapUSDN.vy): Curve stablecoin AMM contract
* [`DepositUSDN`]

## Deployments

<!--
* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [](https://etherscan.io/address/)
* [`DepositUSDN`](DepositUSDN.vy): [](https://etherscan.io/address/)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [](https://etherscan.io/address/)
* [`StableSwapUSDN`](StableSwapUSDT.vy): [](https://etherscan.io/address/)
 -->

## Stablecoins

Curve USDN metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between USDN and the Curve tri-pool LP token.

* `USDN`: [0x674C6Ad92Fd080e4004b2312b45f796a192D27a0](https://etherscan.io/address/0x674C6Ad92Fd080e4004b2312b45f796a192D27a0)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between USDN and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
