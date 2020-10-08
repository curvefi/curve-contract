# curve-contract/contracts/pools/musd

[Curve MUSD metapool](https://www.curve.fi/musd), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositMUSD`](DepositMUSD.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapMUSD`](StableSwapMUSD.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [](https://etherscan.io/address/)
* [`DepositMUSD`](DepositMUSD.vy): [](https://etherscan.io/address/)
* [`StableSwapMUSD`](StableSwapMUSD.vy): [](https://etherscan.io/address/)

## Stablecoins

Curve MUSD metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between MUSD and the Curve tri-pool LP token.

* `MUSD`: [0xe2f2a5C287993345a840Db3B0845fbC70f5935a5](https://etherscan.io/address/0x1c48f86ae57291f7686349f12601910bd8d470bb)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between MUSD and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
