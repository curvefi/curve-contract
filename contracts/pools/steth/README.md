# curve-contract/contracts/pools/steth

[Curve stETH pool](https://www.curve.fi/steth). This is a no-lending pool.

## Contracts

* [`StableSwapSTETH`](StableSwapSTETH.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0x06325440D014e39736583c165C2963BA99fAf14E](https://etherscan.io/address/0x06325440D014e39736583c165C2963BA99fAf14E)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0x182B723a58739a9c974cFDB385ceaDb237453c28](https://etherscan.io/address/0x182B723a58739a9c974cFDB385ceaDb237453c28)
* [`StableSwapSTETH`](StableSwapSTETH.vy): [0xDC24316b9AE028F1497c275EB9192a3Ea0f67022](https://etherscan.io/address/0xDC24316b9AE028F1497c275EB9192a3Ea0f67022)

## Stablecoins

Curve stETH pool supports swaps between Ether and Lido staked ETH.

* `ETH`: represented in the pool as `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`
* `stETH`: [0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84](https://etherscan.io/address/0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84)
