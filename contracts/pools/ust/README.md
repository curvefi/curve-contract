# curve-contract/contracts/pools/ust

[Curve UST metapool](https://www.curve.fi/ust), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositUST`](DepositUST.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapUST`](StableSwapUST.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0x94e131324b6054c0D789b190b2dAC504e4361b53](https://etherscan.io/address/0x94e131324b6054c0D789b190b2dAC504e4361b53)
* [`DepositUST`](DepositUST.vy): [0xB0a0716841F2Fc03fbA72A891B8Bb13584F52F2d](https://etherscan.io/address/0xB0a0716841F2Fc03fbA72A891B8Bb13584F52F2d)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0x3B7020743Bc2A4ca9EaF9D0722d42E20d6935855](https://etherscan.io/address/0x3B7020743Bc2A4ca9EaF9D0722d42E20d6935855)
* [`StableSwapUST`](StableSwapUST.vy): [0x890f4e345B1dAED0367A877a1612f86A1f86985f](https://etherscan.io/address/0x890f4e345B1dAED0367A877a1612f86A1f86985f)

## Stablecoins

Curve UST metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between UST and the Curve tri-pool LP token.

* `UST`: [0xa47c8bf37f92aBed4A126BDA807A7b7498661acD](https://etherscan.io/address/0xa47c8bf37f92aBed4A126BDA807A7b7498661acD)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between UST and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
