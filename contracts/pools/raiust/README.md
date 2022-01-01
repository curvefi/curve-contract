# curve-contract/contracts/pools/raiust

[Curve RAI/UST Pool](): Two coins pool which includes RAI(non-peggie) and UST(peggie) with 18 decimals. 

## Contracts

* [`StableSwapRaiUst`](StableSwapRaiUst.vy): Curve stablecoin AMM contract to swap between a non-peggie(RAI) and a peggie(UST), without lending. 

## Stablecoins

Curve RAI/UST pool supports swaps between the following stablecoins:

* `RAI`: [0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919](https://etherscan.io/address/0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919)
* `UST`: [0xa47c8bf37f92aBed4A126BDA807A7b7498661acD](https://etherscan.io/address/0xa47c8bf37f92aBed4A126BDA807A7b7498661acD)
