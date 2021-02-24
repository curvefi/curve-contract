# curve-contract/contracts/pools/usdp

[Curve USDP metapool](https://www.curve.fi/usdp), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositUSDP`](DepositUSDP.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapUSDP`](StableSwapUSDP.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0x7Eb40E450b9655f4B3cC4259BCC731c63ff55ae6](https://etherscan.io/address/0x7Eb40E450b9655f4B3cC4259BCC731c63ff55ae6)
* [`DepositUSDP`](DepositUSDP.vy): [0x3c8cAee4E09296800f8D29A68Fa3837e2dae4940](https://etherscan.io/address/0x3c8cAee4E09296800f8D29A68Fa3837e2dae4940)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0x055be5DDB7A925BfEF3417FC157f53CA77cA7222](https://etherscan.io/address/0x055be5DDB7A925BfEF3417FC157f53CA77cA7222)
* [`StableSwapUSDP`](StableSwapUSDP.vy): [0x42d7025938bEc20B69cBae5A77421082407f053A](https://etherscan.io/address/0x42d7025938bEc20B69cBae5A77421082407f053A)

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
