# curve-contract/contracts/pools/y

[Curve "Snow" pool](https://www.curve.fi/y), for efficient swaps of [yVault](https://feel-the-yearn.app/vaults) tokens ☃️

This pool is still under development.

## Contracts

* [`DepositSnow`](DepositSnow.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool.
* [`StableSwapSnow`](StableSwapSnow.vy): Curve stablecoin AMM contract

## Deployments
<!-- * [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [](https://etherscan.io/address/)
* [`DepositSnow`](DepositSnow.vy): [](https://etherscan.io/address/)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [](https://etherscan.io/address/)
* [`StableSwapSnow`](StableSwapSnow.vy): [](https://etherscan.io/address/) -->

## Stablecoins

Curve Snow pool supports swaps between the following stablecoins:

* `yvDAI`: [0xACd43E627e64355f1861cEC6d3a6688B31a6F952](https://etherscan.io/address/0xACd43E627e64355f1861cEC6d3a6688B31a6F952)
* `yvUSDC`: [0x597aD1e0c13Bfe8025993D9e79C69E1c0233522e](https://etherscan.io/address/0x597aD1e0c13Bfe8025993D9e79C69E1c0233522e)
* `yvUSDT`: [0x2f08119C6f07c006695E079AAFc638b8789FAf18](https://etherscan.io/address/0x2f08119C6f07c006695E079AAFc638b8789FAf18)
* `yvTUSD`: [0x37d19d1c4E1fa9DC47bD1eA12f742a0887eDa74a](https://etherscan.io/address/0x37d19d1c4E1fa9DC47bD1eA12f742a0887eDa74a)
* `yvyCRV`: [0x5dbcF33D8c2E976c6b560249878e6F1491Bca25c](https://etherscan.io/address/0x5dbcF33D8c2E976c6b560249878e6F1491Bca25c)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
