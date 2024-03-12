# curve-contract/contracts/pools/pax

[Curve PAX pool](https://www.curve.fi/pax), with lending on [yearn.finance](https://yearn.finance/).

## Contracts

* [`DepositPAX`](DepositPAX.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapPAX`](StableSwapPAX.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV1`](../../tokens/CurveTokenV1.vy): [0xD905e2eaeBe188fc92179b6350807D8bd91Db0D8](https://etherscan.io/address/0xD905e2eaeBe188fc92179b6350807D8bd91Db0D8)
* [`DepositPAX`](DepositPAX.vy): [0xa50ccc70b6a011cffddf45057e39679379187287](https://etherscan.io/address/0xa50ccc70b6a011cffddf45057e39679379187287)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [0x64E3C23bfc40722d3B649844055F1D51c1ac041d](https://etherscan.io/address/0x64E3C23bfc40722d3B649844055F1D51c1ac041d)
* [`StableSwapPAX`](StableSwapPAX.vy): [0x06364f10B501e868329afBc005b3492902d6C763](https://etherscan.io/address/0x06364f10B501e868329afBc005b3492902d6C763)

## Stablecoins

Curve PAX pool supports swaps between the following stablecoins:

### Wrapped

* `ycDAI`: [0x99d1fa417f94dcd62bfe781a1213c092a47041bc](https://etherscan.io/address/0x99d1fa417f94dcd62bfe781a1213c092a47041bc)
* `ycUSDC`: [0x9777d7e2b60bb01759d0e2f8be2095df444cb07e](https://etherscan.io/address/0x9777d7e2b60bb01759d0e2f8be2095df444cb07e)
* `ycUSDT`: [0x1be5d71f2da660bfdee8012ddc58d024448a0a59](https://etherscan.io/address/0x1be5d71f2da660bfdee8012ddc58d024448a0a59)

### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
* `PAX`: [0x8e870d67f660d95d5be530380d0ec0bd388289e1](https://etherscan.io/address/0x8e870d67f660d95d5be530380d0ec0bd388289e1)
