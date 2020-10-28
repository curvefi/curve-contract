# curve-contract/contracts/pools/gusd

[Curve GUSD metapool](https://www.curve.fi/gusd), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositGUSD`](DepositGUSD.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapGUSD`](StableSwapGUSD.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0xD2967f45c4f384DEEa880F807Be904762a3DeA07](https://etherscan.io/address/0xD2967f45c4f384DEEa880F807Be904762a3DeA07)
* [`DepositGUSD`](DepositGUSD.vy): [0x64448B78561690B70E17CBE8029a3e5c1bB7136e](https://etherscan.io/address/0x64448B78561690B70E17CBE8029a3e5c1bB7136e)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [0xC5cfaDA84E902aD92DD40194f0883ad49639b023](https://etherscan.io/address/0xC5cfaDA84E902aD92DD40194f0883ad49639b023)
* [`StableSwapGUSD`](StableSwapGUSD.vy): [0x4f062658EaAF2C1ccf8C8e36D6824CDf41167956](https://etherscan.io/address/0x4f062658EaAF2C1ccf8C8e36D6824CDf41167956)

## Stablecoins

Curve GUSD metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between GUSD and the Curve tri-pool LP token.

* `GUSD`: [0x056fd409e1d7a124bd7017459dfea2f387b6d5cd](https://etherscan.io/address/0x056fd409e1d7a124bd7017459dfea2f387b6d5cd)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between GUSD and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
