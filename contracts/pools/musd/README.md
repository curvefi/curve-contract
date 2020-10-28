# curve-contract/contracts/pools/musd

[Curve MUSD metapool](https://www.curve.fi/musd), allowing swaps via the Curve [tri-pool](../3pool).

## Contracts

* [`DepositMUSD`](DepositMUSD.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapMUSD`](StableSwapMUSD.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0x1AEf73d49Dedc4b1778d0706583995958Dc862e6](https://etherscan.io/address/0x1AEf73d49Dedc4b1778d0706583995958Dc862e6)
* [`DepositMUSD`](DepositMUSD.vy): [0x803A2B40c5a9BB2B86DD630B274Fa2A9202874C2](https://etherscan.io/address/0x803A2B40c5a9BB2B86DD630B274Fa2A9202874C2)
* [`LiquidityGaugeReward`](LiquidityGaugeReward): [0x5f626c30EC1215f4EdCc9982265E8b1F411D1352](https://etherscan.io/address/0x5f626c30EC1215f4EdCc9982265E8b1F411D1352)
* [`StableSwapMUSD`](StableSwapMUSD.vy): [0x8474DdbE98F5aA3179B3B3F5942D724aFcdec9f6](https://etherscan.io/address/0x8474DdbE98F5aA3179B3B3F5942D724aFcdec9f6)

## Stablecoins

Curve MUSD metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between MUSD and the Curve tri-pool LP token.

* `MUSD`: [0xe2f2a5C287993345a840Db3B0845fbC70f5935a5](https://etherscan.io/address/0xe2f2a5C287993345a840Db3B0845fbC70f5935a5)
* `3CRV`: [0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490](https://etherscan.io/address/0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490)

## Base Pool coins

The tri-pool LP token may be wrapped or unwrapped to provide swaps between MUSD and the following stablecoins:

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/address/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
