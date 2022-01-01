# curve-contract/contracts/pools/rai

[Curve RAI metapool](https://www.curve.fi/rai), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositRAI`](DepositRAI.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapRAI`](StableSwapRAI.vy): Curve stablecoin AMM contract

## Stablecoins

Curve RAI metapool supports swaps between the following assets:

### Direct swaps

Direct swaps are possible between RAI and the Curve tri-pool LP token.
0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919
* `RAI`: [0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919](https://etherscan.io/address/0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

### Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between RAI and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
