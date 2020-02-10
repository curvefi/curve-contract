# How to integrate Curve smart contracts

First of all, you'll need to know the contract's
[ABI](https://github.com/curvefi/curve-contract/blob/compounded/deployed/2020-01-21_mainnet/swap.abi).
Addresses of the contract and the token representing liquidity are
[here](https://github.com/curvefi/curve-contract/blob/compounded/deployed/2020-01-21_mainnet/mainnet.log).

Next is the breif description of methods you need to fascilitate exchanges.

## Getting static information

```python
coins: public(address[N_COINS])
```
- By calling `contract.coins(i)`, you get contract address of i-th c-token
  (cDAI, cUSDC, ...); `i = 0, 1, ...`.

```python
underlying_coins: public(address[N_COINS])
```
- By calling `contract.underlying_coins(i)`, you get contract address of i-th token
  (DAI, USDC, ...).

Both those methods don't change the state.

## Getting price for c-tokens (cDAI, cUSDC)

```python
def get_dy(i: int128, j: int128, dx: uint256) -> uint256:
```

How much of c-token `j` you'll get in exchange for `dx` of c-token `i`,
including the fee. For example, `get_dy(0, 1, dx)` will give you amount of cUSDC
you'll get for `dx` of cDAI.

This method doesn't change the state.

## Getting price for underlying tokens (DAI, USDC)

```python
def get_dy_underlying(i: int128, j: int128, dx: uint256) -> uint256:
```

How much of underlying token `j` you'll get in exchange for `dx` of token `i`,
including the fee. For example, `get_dy_underlying(0, 1, dx)` will give you amount of USDC
you'll get for `dx` of DAI.

This method doesn't change the state.

## Exchanging c-tokens

```python
def exchange(i: int128, j: int128, dx: uint256, min_dy: uint256):
```

This method exchanges `dx` of c-token `i` into c-token `j`.
You specify `min_dy` as the minimal amount of c-token `j` to get to avoid
front-running. You can also use `deadline` to make transaction revert if it
wasn't accepted for too long.

Used to exchange `cDAI<>cUSDC` (and analogues in future deployments).

## Exchanging underlying tokens

```python
def exchange_underlying(i: int128, j: int128, dx: uint256, min_dy: uint256):
```

This method exchanges `dx` of underlying token `i` into token `j`.
You specify `min_dy` as the minimal amount of token `j` to get to avoid
front-running. You can also use `deadline` to make transaction revert if it
wasn't accepted for too long.

Used to exchange `DAI<>USDC` (and analogues in future deployments).

## Bonus: measuring profits

```python
def get_virtual_price() -> uint256:
```

This read-only methods calculates price of liquidity share. In order to
calculate profits between two points, you measure virtual price in those two
moments and divide later by the earlier, and subtract 1.

The method doesn't measure the real price in dollars, but rather profit on top
of what you would have observe with fee-less exchange. It is not affected by
market fluctuations, and can measure returns even in a volatile market, over any
periods of time.
