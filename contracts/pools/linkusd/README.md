# curve-contract/contracts/pools/linkusd

[Curve LINKUSD metapool](https://www.curve.fi/linkusd), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositLinkUSD`](DepositLinkUSD.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapLinkUSD`](StableSwapLinkUSD.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0x6D65b498cb23deAba52db31c93Da9BFFb340FB8F](https://etherscan.io/address/0x6D65b498cb23deAba52db31c93Da9BFFb340FB8F)
* [`DepositLinkUSD`](DepositGUSD.vy): [0x1de7f0866e2c4adAC7b457c58Cc25c8688CDa1f2](https://etherscan.io/address/0x1de7f0866e2c4adAC7b457c58Cc25c8688CDa1f2)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [](https://etherscan.io/address/)
* [`StableSwapLinkUSD`](StableSwapUSDT.vy): [0xE7a24EF0C5e95Ffb0f6684b813A78F2a3AD7D171](https://etherscan.io/address/0xE7a24EF0C5e95Ffb0f6684b813A78F2a3AD7D171)

## Stablecoins

Curve LINKUSD metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between LINKUSD and the Curve tri-pool LP token.

* `LINKUSD`: [0x0E2EC54fC0B509F445631Bf4b91AB8168230C752](https://etherscan.io/address/0x0E2EC54fC0B509F445631Bf4b91AB8168230C752)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between LINKUSD and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
