# curve-contract/contracts/pools/busd

[Curve BUSD pool](https://www.curve.fi/busd), with lending on [yearn.finance](https://yearn.finance/).

## Contracts

* [`DepositBUSD`](DepositBUSD.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapBUSD`](StableSwapBUSD.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV1`](../../tokens/CurveTokenV1.vy): [0x3B3Ac5386837Dc563660FB6a0937DFAa5924333B](https://etherscan.io/address/0x3B3Ac5386837Dc563660FB6a0937DFAa5924333B)
* [`DepositBUSD`](DepositBUSD.vy): [0xb6c057591e073249f2d9d88ba59a46cfc9b59edb](https://etherscan.io/address/0xb6c057591e073249f2d9d88ba59a46cfc9b59edb)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [0x69Fb7c45726cfE2baDeE8317005d3F94bE838840](https://etherscan.io/address/0x69fb7c45726cfe2badee8317005d3f94be838840)
* [`StableSwapBUSD`](StableSwapBUSD.vy): [0x79a8C46DeA5aDa233ABaFFD40F3A0A2B1e5A4F27](https://etherscan.io/address/0x79a8C46DeA5aDa233ABaFFD40F3A0A2B1e5A4F27)

## Stablecoins

Curve BUSD pool supports swaps between the following stablecoins:

### Wrapped

* `yDAI`: [0xc2cb1040220768554cf699b0d863a3cd4324ce32](https://etherscan.io/address/0xc2cb1040220768554cf699b0d863a3cd4324ce32)
* `yUSDC`: [0x26ea744e5b887e5205727f55dfbe8685e3b21951](https://etherscan.io/address/0x26ea744e5b887e5205727f55dfbe8685e3b21951)
* `yUSDT`: [0xe6354ed5bc4b393a5aad09f21c46e101e692d447](https://etherscan.io/address/0xe6354ed5bc4b393a5aad09f21c46e101e692d447)
* `yBUSD`: [0x04bc0ab673d88ae9dbc9da2380cb6b79c4bca9ae](https://etherscan.io/address/0x04bc0ab673d88ae9dbc9da2380cb6b79c4bca9ae)

### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
* `BUSD`: [0x4fabb145d64652a948d72533023f6e7a623c7c53](https://etherscan.io/address/0x4fabb145d64652a948d72533023f6e7a623c7c53)
