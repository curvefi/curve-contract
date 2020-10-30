# curve-contract/tests/fixtures

Pytest fixtures used in Curve's test suite.

## Files

* [`accounts.py`](accounts.py): Convenience fixtures to aid readability when accessing specific accounts
* [`coins.py`](coins.py): Deployment fixtures for stablecoins and LP tokens
* [`deployments.py`](deployments.py): Deployment fixtures for pools, depositors and other contracts
* [`functions.py`](functions.py): Functions-as-fixtures, used to standardize contract interactions or to access commonly needed functionality
* [`pooldata.py`](pooldata.py): Pool dependent data fixtures
* [`setup.py`](setup.py): Test setup fixtures, used for common processes such as adding initial liquidity or approving token transfers

## Fixtures

### `accounts.py`

Session scoped convenience fixtures providing access to specific unlocked accounts. These are used to aid readability within the test suite.

* `alice`: Yields `web3.eth.accounts[0]`. This is also the deployer address for all contracts.
* `bob`: Yields `web3.eth.accounts[1]`.
* `charlie`: Yields `web3.eth.accounts[2]`.

### `coins.py`

Module scoped deployment fixtures for stablecoins and pool LP tokens.

* `pool_token`: [`CurveToken`](../../contracts/tokens) deployment for the active pool.
* `underlying_coins`: A list of mocked token contracts representing the underlying coins in the active pool. When the pool being tested is a metapool, this list includes the underlying assets for the base pool - NOT the base pool LP token.
* `wrapped_coins`: A list of mocked token contracts representing the wrapped coins in the active pool. The contract used is determined based on `pooldata.json` for the active pool. For pools without lending, these are the same deployments as `underlying_coins`.

### `deployments.py`

Module scoped contract deployment fixtures.

All deployment fixtures are [parametrized](https://docs.pytest.org/en/stable/parametrize.html) to work with every pool in [`contracts/pools`](../../contracts/pools). To add a new pool to the test suite, create a `pooldata.json` in the same subdirectory. You can read about the structure of this JSON file [here](../../contracts/pools/README.md).

* `swap`: [`StableSwap`](../../contracts/pool-templates) deployment for the pool being tested.
* `zap`: [`Deposit`](../../contracts/pool-templates) deployment for the pool being tested.

### `functions.py`

Fixtures-as-functions that are used to standardize contract interafces or access commonly needed functionality.

* `approx`: Comparison function for confirming that two numbers are equal within a relative precision.
* `get_admin_balances`: Function for querying the current admin balances of the active `swap` deployment. This is required because some older pool contracts do not include an `admin_balances` function.
* `set_fees`: Commits and applies a fee and admin fee change to the active `swap` deployment. Because the fee change has a time delay, calling this method advances time by three days.

### `pooldata.py`

Data fixtures for accessing information about the pool currently being tested.

* `underlying_decimals`: A list of decimal values for each deployment in `underlying_coins`.
* `wrapped_decimals`: A list of decimal values for each deployment in `wrapped_coins`.
* `base_amount`: The base amount of each coin that is minted when providing initial liquidity, given without any decimal places.
* `initial_amounts`: A list of values equivalent to `base_amount * 10**decimals` for each deployment in `wrapped_coins`. Used for minting and providing initial liquidity.
* `n_coins`: The number of coins in the active `swap` deployment.

### `setup.py`

Module scoped setup fixtures, used for common processes such as adding initial liquidity or approving token transfers.

Setup fixtures are commonly applied using [`pytestmark`](https://docs.pytest.org/en/latest/reference.html#globalvar-pytestmark) and the [`usefixtures`](https://docs.pytest.org/en/latest/reference.html#pytest-mark-usefixtures) marker:

```python
pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob")
```

* `add_initial_liquidity`: Mints and approves `initial_amounts` coins for `alice` and adds them to `swap` to provide initial liquidity.
* `approve_alice`: Approves `swap` for unlimited transfers of all underlying and wrapped coins from `alice`.
* `approve_bob`:Approves `swap` for unlimited transfers of all underlying and wrapped coins from `bob`.
* `approve_zap`: Approves `zap` for unlimited transfers of `pool_token` and all coins and from `alice` and `bob`.
* `mint_alice`: Mints `initial_amounts` of each underlying and wrapped coin for `alice`.
* `mint_bob`: Mints `initial_amounts` of each underlying and wrapped coin for `bob`.
