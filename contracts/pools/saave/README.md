# curve-contract/contracts/pools/saave

[Curve SAAVE pool](https://www.curve.fi/saave), with lending on [Aave](https://aave.com/).

## Contracts

* [`StableSwapSAAVE`](StableSwapSAAVE.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0x02d341CcB60fAaf662bC0554d13778015d1b285C](https://etherscan.io/address/0x02d341CcB60fAaf662bC0554d13778015d1b285C)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0x462253b8F74B72304c145DB0e4Eebd326B22ca39](https://etherscan.io/address/0x462253b8F74B72304c145DB0e4Eebd326B22ca39)
* [`StableSwapSAAVE`](StableSwapSAAVE.vy): [0xeb16ae0052ed37f479f7fe63849198df1765a733](https://etherscan.io/address/0xeb16ae0052ed37f479f7fe63849198df1765a733)

## Stablecoins

Curve SAAVE pool supports swaps between the following stablecoins:

### Wrapped

* `aDAI`: [0x028171bCA77440897B824Ca71D1c56caC55b68A3](https://etherscan.io/address/0x028171bCA77440897B824Ca71D1c56caC55b68A3)
* `aSUSD`: [0x6c5024cd4f8a59110119c56f8933403a539555eb](https://etherscan.io/address/0x6c5024cd4f8a59110119c56f8933403a539555eb)

### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `sUSD`: [0x57ab1ec28d129707052df4df418d58a2d46d5f51](https://etherscan.io/token/0x57ab1ec28d129707052df4df418d58a2d46d5f51)
