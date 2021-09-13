# Adapting Curve for RAI

This file provides documentation for the pull request to Adapt Curve V1 Contracts so a RAI pool can be used as described
at [gitcoin](https://gitcoin.co/issue/reflexer-labs/curve-contract/1/100026434).

## Licence

All changes are made under the (c) Curve.Fi, 2020 [licence](LICENSE)

## Description of Modifications

The RAI pool created here is built from the meta template with adaptions to handle RAIs moving redemption
price. 3pool is used as the base pool, so RAI will be traded vs 3CRV and the underlying pegged coins. By being a 3pool
metapool it exposes RAI to the three largest relevant assets and makes providing liquidity more attractive as 3pool fees
can be earned at the same time. The meta template was also more amenable to the addition of a new asset type with a
moving redemption price. In the calculation of the StableSwap invariant in the
[meta swap template](contracts/pool-templates/meta/SwapTemplateMeta.vy) there is already a mechanism to scale the
quantity of the base pools LP token by its virtual price, by extending this mechanism to use RAI's redemption price in
the same way we can adapt the meta template to handle RAI with relatively small changes from the already well battle
tested and audited contract.

### Contracts

To view the changes made for rai from vanilla curve [contracts/pools/rai](contracts/pools/rai) should be compared to
[contracts/pool-templates/meta](contracts/pool-templates/meta).

[DepositRAI.vy](contracts/pools/rai/DepositRAI.vy): Set constants, allows users to deposit underlying 3CRV tokens. The
meta template version of this has good separation between the pool and meta sides of the process so no extra
customisations were needed.

[pooldata.json](contracts/pool-templates/meta/pooldata.json): Filled in available constants, after deployments the 0x0
addresses should be replaced.

[README.md](contracts/pools/rai/README.md): Deployment addresses should be added to this later.

[StableSwapRAI.vy](contracts/pools/rai/StableSwapRAI.vy): This contains the core adaptions which make it possible to
use a stablecoin like RAI in curve. Descriptions of key changes:

#### State Variables:
Added an interface for the RAI redemption price snapshot 
[contract](https://github.com/reflexer-labs/geb-redemption-price-snap/blob/master/src/RedemptionPriceSnap.sol) which
exposes the auto generated snappedRedemptionPrice getter method. Also removed redundant rates and precision_mul 
constants as they're now replaced with dynamic values.

####__init__():
Added an additional input argument so the redemption_price_snap address can be stored.

####_get_scaled_redemption_price(): 
New view method which is used to read the redemption price from the snapshot and scale it to the precision used in this
stableswap pool. This is called from many other view methods so a read only method simplifies things, avoids surprise
slippage and min_dy errors, saves gas in trade txs and removes need for special treatment in curve web UI.

####_xp():
This weights the quantity of tokens by their value with element-wise multiplication. Previously it was mainly used to
allow pools of coins with differing levels of precision set in RATES, and in the meta template a token with a virtual
price. This modification extends the mechanism so the quantities are multiplied by a list of 
[redemption_price, virtual_price] which gives a result that works for the D component of curves StableSwap calculation.
The RATES constant became obsolete and has been removed.

####_xp_mem:
Memento or pure version of _xp(). Same as above but with balances and redemption price passed in.

####_get_D_mem:
Adapted to also pass redemption price.

####calc_token_amount():
The change in supply of LP tokens after a deposit or withdrawal is dependent upon the redemption price as it effectively
changes ratio of the two assets. So now this also passes in the redemption price to the D calculation.

####add_liquidity(), get_dy():
Also now dependent on redemption price. Reads it to provide to D/_xp calculations.

####get_dy_underlying():
This method didn't use RATES like the others so there is a more significant change here. Additions added to account for 
redemption price both when the sending or receiving coin is the redemption coin. Also removed code which became
unnecessary after removal of redundant const PRECISION_MUL, consistent change with other pools.

####exchange(), exchange_underlying(), remove_liquidity_imbalance(), _calc_withdraw_one_coin():
Also now dependent on redemption price. Reads it to pass to D/_xp calculations.

### Tests

The new RAI pool is covered by all preexisting meta and common tests, this works because the mock redemption price
snapshot contract is initialised to give a redemption price of 1.0. Additional tests focussing on moving the redemption
price and exercising relevant areas have been added at [tests/pools/rai](tests/pools/rai). RAI pool tests can be run
with "brownie test --pool rai" after following Curve's setup instructions. Descriptions by file of the new tests and
their coverage:

[test_add_liquidity_initial_moving_rp.py](tests/pools/rai/unitary/test_add_liquidity_initial_moving_rp.py): Does not
use the standard fixture to add the initial liquidity and instead adds it after modifying the redemption price. Checks
that the correct amount of pool tokens are minted and awarded and that the min_amount of LP tokens gained takes into
account the redemption price. Also makes sure the modified redemption price doesn't allow depositing of zero on one side
of the first deposit.

[test_add_liquidity_moving_rp.py](tests/pools/rai/unitary/test_add_liquidity_moving_rp.py): Initial liquidity is already
added by the add_initial_liquidity fixture. This test modifies the redemption price before adding additional liquidity
and ensures the depositor is awarded a fair quantity of pool tokens. It tests all combinations of higher and lower RP
and single sided deposits on each side.

[test_exchange_moving_rp.py](tests/pools/rai/unitary/test_exchange_moving_rp.py): Swaps RAI for 3CRV at lower, equal and
higher redemption prices to the initial value. Asserts the trade is successful and that Bob loses the RAI and gains the
correct quantity of 3CRV. It then swaps in the reverse direction and makes sure the result is correct that way too.

[test_exchange_underlying_moving_rp.py](tests/pools/rai/unitary/test_exchange_underlying_moving_rp.py): Tests trades
between underlying 3pool tokens and RAI after modifying the redemption price and checks results are correct considering
redemption price. Also checks get_dy_underlying gives correct value for changes in redemption price.

[test_remove_liquidity_imbalance_moving_rp.py](tests/pools/rai/unitary/test_remove_liquidity_imbalance_moving_rp.py):
This test is run with all permutations of the side removing half the liquidity and causing an imbalance by lowering or
raising the redemption price. It makes sure the correct amount is removed from the pool and added to the caller, and
then that the correct amount of pool tokens are deducted from the user and burnt. The next tests make sure attempts to
withdraw too much liquidity for the specified max amount of pool tokens to burn fail appropriately with a moving
redemption price.

[test_remove_liquidity_moving_rp.py](tests/pools/rai/unitary/test_remove_liquidity_moving_rp.py): Tests removing equal
portions of liquidity from both sides makes sure the results are independent of the moving redemption price.

[test_rp_caching.py](tests/pools/rai/unitary/test_rp_caching.py): Ensures the redemption price mock contract performs
as expected.

[test_redemption_rate_handling.py](tests/pools/rai/integration/test_redemption_rate_handling.py): This is a stateful
test which performs various permutations of actions including modifying the redemption price. It ensures the integrity
of the base pool by making sure the base pools virtual price only increases.

[deployments.py](tests/fixtures/deployments.py): Added redemption_price_snap fixture for use in swap tests.

[RedemptionPriceSnapMock.sol](contracts/testing/RedemptionPriceSnapMock.sol): A mock of the redemption price 
[contract](https://github.com/reflexer-labs/geb-redemption-price-snap/blob/master/src/RedemptionPriceSnap.sol) which
adds the ability to set the redemption price so tests can manipulate it.