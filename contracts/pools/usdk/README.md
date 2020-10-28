# curve-contract/contracts/pools/usdk

[Curve USDK metapool](https://www.curve.fi/usdk), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositUSDK`](DepositUSDK.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapUSDK`](StableSwapUSDK.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0x97E2768e8E73511cA874545DC5Ff8067eB19B787](https://etherscan.io/address/0x97E2768e8E73511cA874545DC5Ff8067eB19B787)
* [`DepositUSDK`](DepositUSDK.vy): [0xF1f85a74AD6c64315F85af52d3d46bF715236ADc](https://etherscan.io/address/0xF1f85a74AD6c64315F85af52d3d46bF715236ADc)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [0xC2b1DF84112619D190193E48148000e3990Bf627](https://etherscan.io/address/0xC2b1DF84112619D190193E48148000e3990Bf627)
* [`StableSwapUSDK`](StableSwapUSDK.vy): [0x3E01dD8a5E1fb3481F0F589056b428Fc308AF0Fb](https://etherscan.io/address/0x3E01dD8a5E1fb3481F0F589056b428Fc308AF0Fb)

## Stablecoins

Curve USDK metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between USDK and the Curve tri-pool LP token.

* `USDK`: [0x1c48f86ae57291f7686349f12601910bd8d470bb](https://etherscan.io/address/0x1c48f86ae57291f7686349f12601910bd8d470bb)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between USDK and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
