# @version 0.2.8
"""
@title Liquidity Gauge v2
@author Curve Finance
@license MIT
"""

from vyper.interfaces import ERC20


event Deposit:
    provider: indexed(address)
    value: uint256

event Withdraw:
    provider: indexed(address)
    value: uint256


MAX_REWARDS: constant(uint256) = 8

lp_token: public(address)

balanceOf: public(HashMap[address, uint256])
totalSupply: public(uint256)


# For tracking external rewards
reward_contract: public(address)
reward_tokens: public(address[MAX_REWARDS])

# deposit / withdraw / claim
reward_sigs: bytes32

# reward token -> integral
reward_integral: public(HashMap[address, uint256])

# reward token -> claiming address -> integral
reward_integral_for: public(HashMap[address, HashMap[address, uint256]])


@external
def __init__(lp_token: address):
    self.lp_token = lp_token


@internal
def _checkpoint_rewards(_addr: address, _total_supply: uint256):
    """
    @notice Claim pending rewards and checkpoint rewards for a user
    """
    if _total_supply == 0:
        return

    balances: uint256[MAX_REWARDS] = empty(uint256[MAX_REWARDS])
    reward_tokens: address[MAX_REWARDS] = empty(address[MAX_REWARDS])
    for i in range(MAX_REWARDS):
        token: address = self.reward_tokens[i]
        if token == ZERO_ADDRESS:
            break
        reward_tokens[i] = token
        balances[i] = ERC20(token).balanceOf(self)

    # claim from reward contract
    raw_call(self.reward_contract, slice(self.reward_sigs, 8, 4))  # dev: bad claim sig

    for i in range(MAX_REWARDS):
        token: address = reward_tokens[i]
        if token == ZERO_ADDRESS:
            break
        dI: uint256 = 10**18 * (ERC20(token).balanceOf(self) - balances[i]) / _total_supply
        if _addr == ZERO_ADDRESS:
            if dI != 0:
                self.reward_integral[token] += dI
            continue

        integral: uint256 = self.reward_integral[token] + dI
        if dI != 0:
            self.reward_integral[token] = integral

        integral_for: uint256 = self.reward_integral_for[token][_addr]
        if integral_for < integral:
            claimable: uint256 = self.balanceOf[_addr] * (integral - integral_for) / 10**18
            self.reward_integral_for[token][_addr] = integral
            assert ERC20(token).transfer(_addr, claimable)


@external
@nonreentrant('lock')
def claimable_reward(_addr: address, _token: address) -> uint256:
    """
    @notice Get the number of claimable reward tokens for a user
    @dev This function should be manually changed to "view" in the ABI
         Calling it via a transaction will claim available reward tokens
    @param _addr Account to get reward amount for
    @param _token Token to get reward amount for
    @return uint256 Claimable reward token amount
    """
    claimable: uint256 = ERC20(_token).balanceOf(_addr)
    if self.reward_contract != ZERO_ADDRESS:
        self._checkpoint_rewards(_addr, self.totalSupply)
    claimable = ERC20(_token).balanceOf(_addr) - claimable

    integral: uint256 = self.reward_integral[_token]
    integral_for: uint256 = self.reward_integral_for[_token][_addr]

    if integral_for < integral:
        claimable += self.balanceOf[_addr] * (integral - integral_for) / 10**18

    return claimable


@external
@nonreentrant('lock')
def claim_rewards(_addr: address = msg.sender):
    """
    @notice Claim available reward tokens for `_addr`
    @param _addr Address to claim for
    """
    self._checkpoint_rewards(_addr, self.totalSupply)


@external
@nonreentrant('lock')
def claim_historic_rewards(_reward_tokens: address[MAX_REWARDS], _addr: address = msg.sender):
    """
    @notice Claim reward tokens available from a previously-set staking contract
    @param _reward_tokens Array of reward token addresses to claim
    @param _addr Address to claim for
    """
    for token in _reward_tokens:
        if token == ZERO_ADDRESS:
            break
        integral: uint256 = self.reward_integral[token]
        integral_for: uint256 = self.reward_integral_for[token][_addr]

        if integral_for < integral:
            claimable: uint256 = self.balanceOf[_addr] * (integral - integral_for) / 10**18
            self.reward_integral_for[token][_addr] = integral
            assert ERC20(token).transfer(_addr, claimable)


@external
@nonreentrant('lock')
def deposit(_value: uint256, _addr: address = msg.sender):
    """
    @notice Deposit `_value` LP tokens
    @dev Depositting also claims pending reward tokens
    @param _value Number of tokens to deposit
    @param _addr Address to deposit for
    """
    if _value != 0:
        reward_contract: address = self.reward_contract
        total_supply: uint256 = self.totalSupply
        if reward_contract != ZERO_ADDRESS:
            self._checkpoint_rewards(_addr, total_supply)

        total_supply += _value
        new_balance: uint256 = self.balanceOf[_addr] + _value
        self.balanceOf[_addr] = new_balance
        self.totalSupply = total_supply

        ERC20(self.lp_token).transferFrom(msg.sender, self, _value)
        if reward_contract != ZERO_ADDRESS:
            deposit_sig: Bytes[4] = slice(self.reward_sigs, 0, 4)
            if convert(deposit_sig, uint256) != 0:
                raw_call(
                    reward_contract,
                    concat(deposit_sig, convert(_value, bytes32))
                )

    log Deposit(_addr, _value)


@external
@nonreentrant('lock')
def withdraw(_value: uint256):
    """
    @notice Withdraw `_value` LP tokens
    @dev Withdrawing also claims pending reward tokens
    @param _value Number of tokens to withdraw
    """
    if _value != 0:
        reward_contract: address = self.reward_contract
        total_supply: uint256 = self.totalSupply
        if reward_contract != ZERO_ADDRESS:
            self._checkpoint_rewards(msg.sender, total_supply)

        total_supply -= _value
        new_balance: uint256 = self.balanceOf[msg.sender] - _value
        self.balanceOf[msg.sender] = new_balance
        self.totalSupply = total_supply

        if reward_contract != ZERO_ADDRESS:
            withdraw_sig: Bytes[4] = slice(self.reward_sigs, 4, 4)
            if convert(withdraw_sig, uint256) != 0:
                raw_call(
                    reward_contract,
                    concat(withdraw_sig, convert(_value, bytes32))
                )
        ERC20(self.lp_token).transfer(msg.sender, _value)

    log Withdraw(msg.sender, _value)


@external
@nonreentrant('lock')
def set_rewards(_reward_contract: address, _sigs: bytes32, _reward_tokens: address[MAX_REWARDS]):
    """
    @notice Set the active reward contract
    @dev A reward contract cannot be set while this contract has no deposits
    @param _reward_contract Reward contract address. Set to ZERO_ADDRESS to
                            disable staking.
    @param _sigs Four byte selectors for staking, withdrawing and claiming,
                 right padded with zero bytes. If the reward contract can
                 be claimed from but does not require staking, the staking
                 and withdraw selectors should be set to 0x00
    @param _reward_tokens List of claimable tokens for this reward contract
    """
    lp_token: address = self.lp_token
    current_reward_contract: address = self.reward_contract
    total_supply: uint256 = self.totalSupply
    if current_reward_contract != ZERO_ADDRESS:
        self._checkpoint_rewards(ZERO_ADDRESS, total_supply)
        withdraw_sig: Bytes[4] = slice(self.reward_sigs, 4, 4)
        if convert(withdraw_sig, uint256) != 0:
            if total_supply != 0:
                raw_call(
                    current_reward_contract,
                    concat(withdraw_sig, convert(total_supply, bytes32))
                )
            ERC20(lp_token).approve(current_reward_contract, 0)

    if _reward_contract != ZERO_ADDRESS:
        assert _reward_contract.is_contract  # dev: not a contract
        sigs: bytes32 = _sigs
        deposit_sig: Bytes[4] = slice(sigs, 0, 4)
        withdraw_sig: Bytes[4] = slice(sigs, 4, 4)

        if convert(deposit_sig, uint256) != 0:
            # need a non-zero total supply to verify the sigs
            assert total_supply != 0  # dev: zero total supply
            ERC20(lp_token).approve(_reward_contract, MAX_UINT256)

            # it would be Very Bad if we get the signatures wrong here, so
            # we do a test deposit and withdrawal prior to setting them
            raw_call(
                _reward_contract,
                concat(deposit_sig, convert(total_supply, bytes32))
            )  # dev: failed deposit
            assert ERC20(lp_token).balanceOf(self) == 0
            raw_call(
                _reward_contract,
                concat(withdraw_sig, convert(total_supply, bytes32))
            )  # dev: failed withdraw
            assert ERC20(lp_token).balanceOf(self) == total_supply

            # deposit and withdraw are good, time to make the actual deposit
            raw_call(
                _reward_contract,
                concat(deposit_sig, convert(total_supply, bytes32))
            )
        else:
            assert convert(withdraw_sig, uint256) == 0  # dev: withdraw without deposit

    self.reward_contract = _reward_contract
    self.reward_sigs = _sigs
    for i in range(MAX_REWARDS):
        if _reward_tokens[i] != ZERO_ADDRESS:
            self.reward_tokens[i] = _reward_tokens[i]
        elif self.reward_tokens[i] != ZERO_ADDRESS:
            self.reward_tokens[i] = ZERO_ADDRESS
        else:
            assert i != 0  # dev: no reward token
            break

    if _reward_contract != ZERO_ADDRESS:
        # do an initial checkpoint to verify that claims are working
        self._checkpoint_rewards(ZERO_ADDRESS, total_supply)
