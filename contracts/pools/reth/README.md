# curve-contract/contracts/pools/reth

[Curve rETH]()

## Contracts

- [`StableSwaprETH`](StableSwapRETH.vy): Curve stablecoin AMM contract

## Deployments

- [`CurveContractV3`](../../tokens/CurveTokenV3.vy):
- [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy):
- [`StableSwapRETH`](StableSwapRETH.vy):

## Stablecoins

Curve rETH pool supports swaps between ETH and [`rETH`](https://github.com/stafiprotocol/) staked ETH (rETH):

- `ETH`: represented in the pool as `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`
- `rETH`: [0x9559aaa82d9649c7a7b220e7c461d2e74c9a3593](https://etherscan.io/token/0x9559aaa82d9649c7a7b220e7c461d2e74c9a3593#code)
