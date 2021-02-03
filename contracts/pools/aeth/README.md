# curve-contract/contracts/pools/aeth

[Curve ankrETH]()

## Contracts

- [`StableSwapAETH`](StableSwapAETH.vy): Curve stablecoin AMM contract

## Deployments

- [`CurveContractV3`](../../tokens/CurveTokenV3.vy):
- [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy):
- [`StableSwapAETH`](StableSwapAETH.vy):

## Stablecoins

Curve aETH pool supports swaps between ETH and [`Ankr`](https://github.com/Ankr-network) staked ETH (aETH):

- `ETH`: represented in the pool as `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`
- `aETH`: [0xE95A203B1a91a908F9B9CE46459d101078c2c3cb](https://etherscan.io/address/0xE95A203B1a91a908F9B9CE46459d101078c2c3cb#code)
