# curve-contract/contracts/pools/y

[Curve "Snow" pool](https://www.curve.fi/y), for efficient swaps of [yVault](https://feel-the-yearn.app/vaults) tokens ☃️

## Contracts

* [`DepositSnow`](DepositSnow.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool.
* [`StableSwapSnow`](StableSwapSnow.vy): Curve stablecoin AMM contract

## Deployments
* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0x3921574E4146fC09701a1B24CFb0f9906e8FEe92](https://etherscan.io/address/0x3921574e4146fc09701a1b24cfb0f9906e8fee92)
* [`DepositSnow`](DepositSnow.vy): [0x2021a9990640c8ff8FcCb553648571D525B53a6e](https://etherscan.io/address/0x2021a9990640c8ff8fccb553648571d525b53a6e)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [0x18478F737d40ed7DEFe5a9d6F1560d84E283B74e](https://etherscan.io/address/0x18478f737d40ed7defe5a9d6f1560d84e283b74e)
* [`StableSwapSnow`](StableSwapSnow.vy): [0xF0f745C81E4533c697cF0104c5EFdCbf84359542](https://etherscan.io/address/0xf0f745c81e4533c697cf0104c5efdcbf84359542#code)


## Stablecoins

Curve Snow pool supports swaps between the following stablecoins:

* `yvDAI`: [0xACd43E627e64355f1861cEC6d3a6688B31a6F952](https://etherscan.io/address/0xACd43E627e64355f1861cEC6d3a6688B31a6F952)
* `yvUSDC`: [0x597aD1e0c13Bfe8025993D9e79C69E1c0233522e](https://etherscan.io/address/0x597aD1e0c13Bfe8025993D9e79C69E1c0233522e)
* `yvUSDT`: [0x2f08119C6f07c006695E079AAFc638b8789FAf18](https://etherscan.io/address/0x2f08119C6f07c006695E079AAFc638b8789FAf18)
* `yvTUSD`: [0x37d19d1c4E1fa9DC47bD1eA12f742a0887eDa74a](https://etherscan.io/address/0x37d19d1c4E1fa9DC47bD1eA12f742a0887eDa74a)
* `yvyCRV`: [0x5dbcF33D8c2E976c6b560249878e6F1491Bca25c](https://etherscan.io/address/0x5dbcF33D8c2E976c6b560249878e6F1491Bca25c)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
