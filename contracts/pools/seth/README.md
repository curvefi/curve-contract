# curve-contract/contracts/pools/seth

[Curve sETH pool](https://www.curve.fi/seth). This is a no-lending pool.

## Contracts

* [`StableSwapSETH`](StableSwapSETH.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0xA3D87FffcE63B53E0d54fAa1cc983B7eB0b74A9c](https://etherscan.io/address/0xA3D87FffcE63B53E0d54fAa1cc983B7eB0b74A9c)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [](https://etherscan.io/address/0x3C0FFFF15EA30C35d7A85B85c0782D6c94e1d238)
* [`StableSwapSETH`](StableSwapSETH.vy): [0xc5424b857f758e906013f3555dad202e4bdb4567](https://etherscan.io/address/0xc5424b857f758e906013f3555dad202e4bdb4567)

## Stablecoins

Curve ETH pool supports swaps between Ether and Synthetix sETH.

* `ETH`: represented in the pool as `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`
* `sETH`: [0x5e74C9036fb86BD7eCdcb084a0673EFc32eA31cb](https://etherscan.io/address/0x5e74C9036fb86BD7eCdcb084a0673EFc32eA31cb)
