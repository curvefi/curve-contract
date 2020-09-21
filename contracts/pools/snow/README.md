# curve-contract/contracts/pools/y

[Curve "Snow" pool](https://www.curve.fi/y), for efficient swaps of [yVault](https://feel-the-yearn.app/vaults) tokens ❄️

## Contracts

* [`DepositSnow`](DepositSnow.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool.
* [`StableSwapSnow`](StableSwapSnow.vy): Curve stablecoin AMM contract

## Deployments
<!--
* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): []()
* [`DepositUSDT`](DepositUSDT.vy): []()
* [`StableSwapUSDT`](StableSwapUSDT.vy): []() -->

## Stablecoins

Curve Snow pool supports swaps between the following stablecoins:

### Wrapped

* `yvDAI`: [0xACd43E627e64355f1861cEC6d3a6688B31a6F952](https://etherscan.io/address/0xACd43E627e64355f1861cEC6d3a6688B31a6F952)
* `yvUSDC`: [0x597aD1e0c13Bfe8025993D9e79C69E1c0233522e](https://etherscan.io/address/0x597aD1e0c13Bfe8025993D9e79C69E1c0233522e)
* `yvUSDT`: [0x2f08119C6f07c006695E079AAFc638b8789FAf18](https://etherscan.io/address/0x2f08119C6f07c006695E079AAFc638b8789FAf18)
* `yvTUSD`: [0x37d19d1c4E1fa9DC47bD1eA12f742a0887eDa74a](https://etherscan.io/address/0x37d19d1c4E1fa9DC47bD1eA12f742a0887eDa74a)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)

<!-- ### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
* `TUSD`: [0x0000000000085d4780b73119b644ae5ecd22b376](https://etherscan.io/address/0x0000000000085d4780b73119b644ae5ecd22b376) -->
