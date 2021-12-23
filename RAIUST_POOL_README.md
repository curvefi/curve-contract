# Adapting Curve Base Pool for RAI

This file provides documentation for the pull request to Adapt Curve V1 Contracts so a non-peggie (such as RAI) and a peggie (such as UST) can be swapped as described at [gitcoin](https://gitcoin.co/issue/reflexer-labs/curve-contract/6/100027296). In order to optimize, the coin in the pool should be with 18 decimals. 

## Licence

All changes are made under the (c) Curve.Fi, 2020 [licence](LICENSE)

## Description of Modifications

Main modification:

The RAIUST pool created here is built from the [template code](https://etherscan.io/address/0x55A8a39bc9694714E2874c1ce77aa1E599461E18#code) with adaptions to handle RAIs moving redemption
price. UST is the peggie coin used in this pool, RAI is the non-peggie coin used in this pool. The price of UST is stable, but the redmeption price of RAI is moving. It is usually necessary to get the latest redemption price snap to calculate the coin's balance and LP Token amount when depositing or withdrawing liquidity. I get the inspiration of fetching RAI's redemption price and redemption price adaption implementaion from the [RAI Metapool code](https://github.com/reflexer-labs/curve-contract/tree/master/contracts/pools/rai) and last [gitcoin project](https://gitcoin.co/issue/reflexer-labs/curve-contract/1/100026434).

Other modifications: 
1) [template code](https://etherscan.io/address/0x55A8a39bc9694714E2874c1ce77aa1E599461E18#code) has been optimized to support only ERC20 coin. I refer to the use of function "raw_call" in [SwapTemplateBase.vy](https://github.com/reflexer-labs/curve-contract/tree/master/contracts/pools-templates/base/SwapTemplateBase.vy) to make the contract support more coins; 
2) [template code](https://etherscan.io/address/0x55A8a39bc9694714E2874c1ce77aa1E599461E18#code) provide LP Token balance by self, it cannot specify LP Token Address. I refer to the use of "CurveToken" in [SwapTemplateBase.vy](https://github.com/reflexer-labs/curve-contract/tree/master/contracts/pools-templates/base/SwapTemplateBase.vy) to support outer LP Token.
3) Added some codes to make the contract satisfy brownie test demand.


## Contracts

To view the changes made for RAIUST from vanilla curve [contracts/pools/raiust/StableSwapRaiust.vy](contracts/pools/raiust/StableSwapRaiust.vy) should be compared to [template code](https://etherscan.io/address/0x55A8a39bc9694714E2874c1ce77aa1E599461E18#code).

[pooldata.json](contracts/pools/raiust/pooldata.json): Filled in available constants, after deployments the 0x0 addresses should be replaced.

[README.md](contracts/pools/raiust/README.md): Introdue RAIUST pool. Deployment addresses should be added to this later.

[StableSwapRaiust.vy](contracts/pools/raiust/StableSwapRaiust.vy): This contains the core adaptions which make it possible swap between a non-peggie (such as RAI) and a peggie (such as UST) in curve. In order to optimize, the coin in the pool should be with 18 decimals. Descriptions of key changes:

#### State Variables:
Added an interface for the RAI redemption price snapshot [contract](https://github.com/reflexer-labs/geb-redemption-price-snap/blob/master/src/RedemptionPriceSnap.sol) which exposes the auto generated snappedRedemptionPrice getter method. 
Added CurveToken interface which can be used to specify the LP Token address.
Added some constants, such as RATES for peggie coin(such as UST) and REDMPTION_PRICE_SCALE for non-peggie coin(such as RAI).
Deleted the lp token state variables in self, such as balanceOf, allowance, totalSupply.

#### __init__():
Added an additional input argument so the redemption_price_snap address can be stored.

#### _get_scaled_redemption_price(): 
New view method which is used to read the redemption price from the snapshot and scale it to the precision used in this stableswap pool. This is called from many other view methods so a read only method simplifies things, avoids surprise slippage and min_dy errors, saves gas in trade txs and removes need for special treatment in curve web UI.

#### _xp():
New view internal method. This weights the quantity of tokens by their value with element-wise multiplication. Previously it was mainly used to allow pools of coins with differing levels of precision set in RATES. This modification extends the mechanism so the quantities are multiplied by a array of [self._get_scaled_redemption_price(), RATES] which gives a result that works for the D component of curves StableSwap calculation.

#### _xp_mem():
New view internal method. Memento or pure version of _xp(). Same as above but with balances passed in.

#### _get_D():
Adpate the internal method. Make the internal method name start from "_". And whenever invoking the method, _xp not the balance is passed in. 

#### _get_D_mem():
New view internal method. Adapted to also pass redemption price.

#### calc_token_amount():
The change in supply of LP tokens after a deposit or withdrawal is dependent upon the redemption price as it effectively changes ratio of the two assets. So now this also passes in the redemption price to the D calculation.

#### add_liquidity():
Amount of LP tokens received by depositing coins into the pool. It also depends on redempton price.

#### _get_dy(), _get_y():
Calculate the current output dy given input dx, or calculate the current output y given input x. Also now dependent on redemption price. 

#### exchange():
Perform an exchange between two coins given the amount dx of coin being exchanged. Also now dependent on redemption price. 

#### remove_liquidity_imbalance():
Withdraw coins from the pool in an imbalanced amount. Also now dependent on redemption price. 

#### _get_y_D():
Calculate the current output y given input two coins' xp and D. Also now dependent on redemption price. 

#### _calc_withdraw_one_coin(), calc_withdraw_one_coin(), remove_liquidity_one_coin():
Withdraw a single coin from the pool. Also now dependent on redemption price. 

## Brownie Test
### Test Code

The new RAIUST pool is covered by all preexisting common tests, this works because the [mock redemption price snapshot contract](contracts/testing/RedemptionPriceSnapMock.sol) is initialised to give a redemption price of 1.0. Additional tests focussing on moving the redemption price and exercising relevant areas have been added at [tests/pools/raiust](tests/pools/raiust). RAIUST pool tests can be run with "brownie test --pool raiust" after following Curve's setup instructions. Reflexer-labs has given [test code for RAI meta pool](https://github.com/reflexer-labs/curve-contract/tree/master/tests/pools/rai/). Although the test code is for meta pool, some of the test codes are still quite useful for base pool test. My test codes refer to both [test code for RAI meta pool](https://github.com/reflexer-labs/curve-contract/tree/master/tests/pools/rai/) and [test code template](https://github.com/reflexer-labs/curve-contract/tree/master/tests/pools/common), and make some modifications of them.   

Descriptions by file of the new tests and their coverage:

[test_add_liquidity_initial_moving_rp_raiust.py](tests/pools/raiust/unitary/test_add_liquidity_initial_moving_rp_raiust.py): Does not use the standard fixture to add the initial liquidity and instead adds it after modifying the redemption price. Checks
that the correct amount of pool tokens are minted and awarded and that the min_amount of LP tokens gained takes into account the redemption price. Also makes sure the modified redemption price doesn't allow depositing of zero on one side of the first deposit.

[test_add_liquidity_moving_rp_raiust.py](tests/pools/raiust/unitary/test_add_liquidity_moving_rp_raiust.py): Initial liquidity is already added by the add_initial_liquidity fixture. This test modifies the redemption price before adding additional liquidity and ensures the depositor is awarded a fair quantity of pool tokens. It tests all combinations of higher and lower RP and single sided deposits on each side.

[test_exchange_moving_rp_raiust.py](tests/pools/raiust/unitary/test_exchange_moving_rp_raiust.py): Swaps RAI for UST at lower, equal and higher redemption prices to the initial value. Asserts the trade is successful and that Bob loses the RAI and gains the correct quantity of UST. It then swaps in the reverse direction and makes sure the result is correct that way too.

[test_remove_liquidity_imbalance_moving_rp_raiust.py](tests/pools/rai/unitary/test_remove_liquidity_imbalance_moving_rp_raiust.py): This test is run with all permutations of the side removing half the liquidity and causing an imbalance by lowering or raising the redemption price. It makes sure the correct amount is removed from the pool and added to the caller, and
then that the correct amount of pool tokens are deducted from the user and burnt. The next tests make sure attempts to withdraw too much liquidity for the specified max amount of pool tokens to burn fail appropriately with a moving redemption price.

[test_remove_liquidity_moving_rp_raiust.py](tests/pools/raiust/unitary/test_remove_liquidity_moving_rp_raiust.py): Tests removing equal portions of liquidity from both sides makes sure the results are independent of the moving redemption price.

[test_rp_caching_raiust.py](tests/pools/raiust/unitary/test_rp_caching_raiust.py): Ensures the redemption price mock contract performs as expected.

[test_rp_moving_raiust.py](tests/pools/raiust/integration/test_redemption_rate_handling_raiust.py): This is a stateful test which performs various permutations of actions including modifying the redemption price. It ensures the integrity of the base pool by making sure the base pools virtual price only increases.

[deployments.py](tests/fixtures/deployments.py): The redemption_price_snap has been added to the file in the forked [reflexer-labs/curve-contract master branch](https://github.com/reflexer-labs/curve-contract). The new pool name "raiust" should be added to pool_data in fixture redemption_price_snap.

### Test Instruction
The test has been done locally. Test environment includes: platform win32 -- Python 3.8.1 eth-brownie-1.17.2 Vyper-0.2.12 Ganache-cli-6.12.2 VisualCode-2021. The contract has passed all default [common integration test](tests/pools/common/integration/) and [common unitary test](tests/pools/common/unitary/). Meanwhile the [specific integration test](tests/pools/raiust/integration/) and [specific unitary test](tests/pools/raiust/unitary/) including the moving redemption price has also gone through. 

To run tests:

```bash
brownie test tests/ --pool raiust
```
