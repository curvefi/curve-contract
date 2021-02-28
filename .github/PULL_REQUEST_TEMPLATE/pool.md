## New Pool Checklist

### Pool Info

* Name:
* Base template: <!-- Add a link to the pool template that you used as a starting point for this pool. -->

<!-- Add a short description here of anything special about this pool that a reviewer should be aware of. -->

### Lending

<!-- If this is not a lending pool, this section may be removed. -->

* Lending protocol being used:
* Link to the protocol source code:
* Link to the developer documentation:

1. This protocol handles interest via: <!-- token balance increases / redemption rate increases / other (describe) -->
2. The process of lending tokens on the platform: <!-- A brief technical description -->
3. The process of redeeming tokens on the platform:
4. Is there a fee charged upon withdrawal, or the capability to charge a withdrawal fee? <!-- If yes, explain how the fee works and how it is handled in the pool. -->

- [ ] I have reviewed the documentation and source code for the lending protocol, checking for unexpected behaviours that could affect the pool.

<!-- If the protocol has any unexpected behaviours that are not mentioned above, explain them here -->

### Tokens

<!-- Replicate the following section once for each wrapped and underlying token within the pool -->

#### <TOKEN_NAME>

**General Info**
* Deployment address:
* Link to the token source code:
* Link to the developer documentation:

**Behaviours**
1. On a successful transfer this token: <!-- returns True / returns None / other (describe) -->
2. On a failed transfer this token: <!-- returns False / reverts / other (describe) -->
3. Are there any special approval behaviors? <!-- Cannot approve more than your balance, cannot do nonzero to nonzero approval, cannot do approval, etc -->
4. Is there a transfer fee, or the capability to add a transfer fee in the future? <!-- If yes, explain how the fee works and how it is handled in the pool. -->

- [ ] I have reviewed the documentation and source code for this token, checking for unexpected behaviours that could affect the pool.

<!-- If the token has any unexpected behaviours that are not mentioned above, explain them here -->

### Incenvites

This pool <WILL / WILL NOT> receive incentives other than CRV.

<!-- If the pool is being incentivized with rewards from one or more teams, provide an explanation of how these rewards will be handled and any additional requirements they create. -->

### Fees

1. Does this pool include tokens that are already handled by the fee burning process? <!-- If yes, include references to the burners -->

2. Does this pool include tokens that are not currently being burned, but which can be handled by an already deployed burner? <!-- If yes, open a pull request modifying unit tests at https://github.com/curvefi/curve-dao-contracts/tree/master/tests/fork/Burners to demonstrate that the current burner(s) are capable -->

3. Does this pool require deployment of any new burners? <!-- If yes, open a pull request adding the new burner(s) to https://github.com/curvefi/curve-dao-contracts/tree/master/contracts/burners with tests to verify they work as expected -->

### Pre-review Checklist

<!-- All of these tasks must be completed prior to marking your PR as ready for review -->

- [ ] I have included a `pooldata.json` with accurate token addresses
- [ ] I have included a `README.md` with accurate token addresses
- [ ] I have added a workflow targetting this pool, and confirmed that all tests are passing within the CI
- [ ] I have run `brownie test tests/forked --network mainnet-fork` locally and confirmed that all tests are passing
- [ ] I have verified the fee burning process for this pool and opened a related pull request on [`curve-dao-contracts`](https://github.com/curvefi/curve-dao-contracts) if needed

### Reviewer Pre-deployment Checklist

<!-- To be completed by the reviewer (NOT the person who opened the pull request) prior to deployment -->

- [ ] This PR contains a new workflow file, and the entire test suite is passing
- [ ] I have verified the success / failure behaviours for each token in this pool
- [ ] I have run `brownie test tests/forked --network mainnet-fork` locally and confirmed that all tests are passing
- [ ] I have verified the fee burning process for this pool and any related pull requests
- [ ] This pool makes no significant modifications to the core math OR has been reviewed personally by [@michwill](https://github.com/michwill)

### Post-deployment Checklist

<!-- To be completed after deployment and prior to merging this pull request -->

- [ ] I have deployed a [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy) contract for this pool
- [ ] I have deployed any required fee burner contracts
- [ ] I have added pool and gauge deployment addresses to the `pooldata.json` and `README.md` files within this PR
- [ ] I have opened a pull request on [`curve-docs`](https://github.com/curvefi/curve-docs) to add the new deployment addresses to the documentation
- [ ] I have [created a DAO vote]((https://github.com/curvefi/curve-dao-contracts/blob/master/scripts/voting/new_vote.py)) to add the new gauge and enable/configure fee burning
