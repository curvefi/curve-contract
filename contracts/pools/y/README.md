# curve-contract/contracts/pools/y

[Curve Y pool](https://www.curve.fi/y), with lending on [yearn.finance](https://yearn.finance/).

## Contracts

* [`DepositY`](DepositY.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool.
* [`StableSwapY`](StableSwapY.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV1`](../../tokens/CurveTokenV1.vy): [0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8](https://etherscan.io/address/0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8)
* [`DepositUSDT`](DepositUSDT.vy): [0xbbc81d23ea2c3ec7e56d39296f0cbb648873a5d3](https://etherscan.io/address/0xbbc81d23ea2c3ec7e56d39296f0cbb648873a5d3)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [0xFA712EE4788C042e2B7BB55E6cb8ec569C4530c1](https://etherscan.io/address/0xfa712ee4788c042e2b7bb55e6cb8ec569c4530c1)
* [`StableSwapUSDT`](StableSwapUSDT.vy): [0x45F783CCE6B7FF23B2ab2D70e416cdb7D6055f51](https://etherscan.io/address/0x45F783CCE6B7FF23B2ab2D70e416cdb7D6055f51)

## Stablecoins

Curve Y pool supports swaps between the following stablecoins:

### Wrapped

* `yDAI`: [0x16de59092dAE5CcF4A1E6439D611fd0653f0Bd01](https://etherscan.io/address/0x16de59092dAE5CcF4A1E6439D611fd0653f0Bd01)
* `yUSDC`: [0xd6aD7a6750A7593E092a9B218d66C0A814a3436e](https://etherscan.io/address/0xd6aD7a6750A7593E092a9B218d66C0A814a3436e)
* `yUSDT`: [0x83f798e925BcD4017Eb265844FDDAbb448f1707D](https://etherscan.io/address/0x83f798e925BcD4017Eb265844FDDAbb448f1707D)
* `yTUSD`: [0x73a052500105205d34daf004eab301916da8190f](https://etherscan.io/address/0x73a052500105205d34daf004eab301916da8190f)

### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
* `TUSD`: [0x0000000000085d4780b73119b644ae5ecd22b376](https://etherscan.io/address/0x0000000000085d4780b73119b644ae5ecd22b376)
