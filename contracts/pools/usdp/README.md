# curve-contract/contracts/pools/usdp

[Curve USDP metapool](https://www.curve.fi/usdp), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositUSDP`](DepositUSDP.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapUSDP`](StableSwapUSDP.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0x86a91b50af95ff1d9d53ca1e4963ef06d8b31369](https://etherscan.io/address/0x86a91b50af95ff1d9d53ca1e4963ef06d8b31369)
* [`DepositUSDP`](DepositUSDP.vy): [0xF7De9c7d406253F1b54dcF5E8BAc5a921219dE09](https://etherscan.io/address/0xF7De9c7d406253F1b54dcF5E8BAc5a921219dE09)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0x174baa6b56ffe479b604cc20f22d09ad74f1ca49](https://etherscan.io/address/0x174baa6b56ffe479b604cc20f22d09ad74f1ca49)
* [`StableSwapUSDP`](StableSwapUSDP.vy): [0x36965b1a6b97c1b33416e5d53fb5621ade1f1e80](https://etherscan.io/address/0x36965b1a6b97c1b33416e5d53fb5621ade1f1e80)

## Stablecoins

Curve USDP metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between USDP and the Curve tri-pool LP token.

* `USDP`: [0x1456688345527bE1f37E9e627DA0837D6f08C925](https://etherscan.io/address/0x1456688345527bE1f37E9e627DA0837D6f08C925)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between USDP and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
