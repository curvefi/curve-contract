# curve-contract/contracts/pools/rsv

[Curve RSV metapool](https://www.curve.fi/rsv), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositRSV`](DepositRSV.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapRSV`](StableSwapRSV.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0xC2Ee6b0334C261ED60C72f6054450b61B8f18E35](https://etherscan.io/address/0xC2Ee6b0334C261ED60C72f6054450b61B8f18E35)
* [`DepositRSV`](DepositRSV.vy): [0xBE175115BF33E12348ff77CcfEE4726866A0Fbd5](https://etherscan.io/address/0xBE175115BF33E12348ff77CcfEE4726866A0Fbd5)
* [`LiquidityGaugeReward`](../../gauges/LiquidityGaugeReward.vy): [0x4dC4A289a8E33600D8bD4cf5F6313E43a37adec7](https://etherscan.io/address/0x4dC4A289a8E33600D8bD4cf5F6313E43a37adec7)
* [`StableSwapRSV`](StableSwapRSV.vy): [0xC18cC39da8b11dA8c3541C598eE022258F9744da](https://etherscan.io/address/0xC18cC39da8b11dA8c3541C598eE022258F9744da)

## Stablecoins

Curve RSV metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between RSV and the Curve tri-pool LP token.

* `RSV`: [0x196f4727526eA7FB1e17b2071B3d8eAA38486988](https://etherscan.io/address/0x196f4727526eA7FB1e17b2071B3d8eAA38486988)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between RSV and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
