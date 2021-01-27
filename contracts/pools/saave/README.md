# curve-contract/contracts/pools/saave

[Curve SAAVE pool](https://www.curve.fi/saave), with lending on [Aave](https://aave.com/).

## Contracts

* [`StableSwapSAAVE`](StableSwapSAAVE.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0xFd2a8fA60Abd58Efe3EeE34dd494cD491dC14900](https://etherscan.io/address/0xFd2a8fA60Abd58Efe3EeE34dd494cD491dC14900)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0xd662908ADA2Ea1916B3318327A97eB18aD588b5d](https://etherscan.io/address/0xd662908ADA2Ea1916B3318327A97eB18aD588b5d)
* [`StableSwapSAAVE`](StableSwapSAAVE.vy): [0xDeBF20617708857ebe4F679508E7b7863a8A8EeE](https://etherscan.io/address/0xDeBF20617708857ebe4F679508E7b7863a8A8EeE)

## Stablecoins

Curve SAAVE pool supports swaps between the following stablecoins:

### Wrapped

* `aDAI`: [0x028171bCA77440897B824Ca71D1c56caC55b68A3](https://etherscan.io/address/0x028171bCA77440897B824Ca71D1c56caC55b68A3)
* `aSUSD`: [0x6c5024cd4f8a59110119c56f8933403a539555eb](https://etherscan.io/address/0x6c5024cd4f8a59110119c56f8933403a539555eb)

### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `sUSD`: [0x57ab1ec28d129707052df4df418d58a2d46d5f51](https://etherscan.io/token/0x57ab1ec28d129707052df4df418d58a2d46d5f51)
