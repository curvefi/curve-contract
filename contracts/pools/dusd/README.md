# curve-contract/contracts/pools/dusd

[Curve DUSD metapool](https://www.curve.fi/dusd), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositDUSD`](DepositDUSD.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapDUSD`](StableSwapDUSD.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0x3a664Ab939FD8482048609f652f9a0B0677337B9](https://etherscan.io/address/0x3a664Ab939FD8482048609f652f9a0B0677337B9)
* [`DepositDUSD`](DepositDUSD.vy): [0x61E10659fe3aa93d036d099405224E4Ac24996d0](https://etherscan.io/address/0x61E10659fe3aa93d036d099405224E4Ac24996d0)
* [`LiquidityGaugeReward`](../../gauges/LiquidityGaugeReward.vy): [0xAEA6c312f4b3E04D752946d329693F7293bC2e6D](https://etherscan.io/address/0xAEA6c312f4b3E04D752946d329693F7293bC2e6D)
* [`StableSwapDUSD`](StableSwapDUSD.vy): [0x8038C01A0390a8c547446a0b2c18fc9aEFEcc10c](https://etherscan.io/address/0x8038C01A0390a8c547446a0b2c18fc9aEFEcc10c)

## Stablecoins

Curve DUSD metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between DUSD and the Curve tri-pool LP token.

* `DUSD`: [0x5bc25f649fc4e26069ddf4cf4010f9f706c23831](https://etherscan.io/address/0x5bc25f649fc4e26069ddf4cf4010f9f706c23831)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between DUSD and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
