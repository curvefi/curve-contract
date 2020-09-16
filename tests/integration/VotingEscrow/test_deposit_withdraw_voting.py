import brownie
from brownie import history, chain
from brownie.test import strategy

WEEK = 86400 * 7
MAX_TIME = 86400 * 365 * 4
GAS_LIMIT = 4_000_000


class StateMachine:

    # account to perform a deposit / withdrawal from
    st_account = strategy('address')

    # amount to deposit / withdraw
    st_value = strategy('uint64')

    # number of weeks to lock a deposit
    st_lock_duration = strategy('uint8')

    # number of weeks to advance the clock
    st_sleep_duration = strategy('uint', min_value=1, max_value=4)

    def __init__(self, accounts, token, voting_escrow):
        self.accounts = accounts
        self.token = token
        self.voting_escrow = voting_escrow

        for acct in accounts:
            token._mint_for_testing(10**40, {'from': acct})
            token.approve(voting_escrow, 2**256-1, {'from': acct})

    def setup(self):
        self.token_balances = {i: 10**40 for i in self.accounts}
        self.voting_balances = {i: {'value': 0, 'unlock_time': 0} for i in self.accounts}

    def rule_create_lock(self, st_account, st_value, st_lock_duration):
        unlock_time = (chain.time() + st_lock_duration * WEEK) // WEEK * WEEK

        if st_value == 0:
            with brownie.reverts("dev: need non-zero value"):
                self.voting_escrow.create_lock(st_value, unlock_time, {'from': st_account, 'gas': GAS_LIMIT})

        elif self.voting_balances[st_account]['value'] > 0:
            with brownie.reverts("Withdraw old tokens first"):
                self.voting_escrow.create_lock(st_value, unlock_time, {'from': st_account, 'gas': GAS_LIMIT})

        elif unlock_time <= chain.time():
            with brownie.reverts("Can only lock until time in the future"):
                self.voting_escrow.create_lock(st_value, unlock_time, {'from': st_account, 'gas': GAS_LIMIT})

        elif unlock_time > chain.time() + 86400 * 365 * 4:
            with brownie.reverts("Voting lock can be 4 years max"):
                self.voting_escrow.create_lock(st_value, unlock_time, {'from': st_account, 'gas': GAS_LIMIT})

        else:
            tx = self.voting_escrow.create_lock(st_value, unlock_time, {'from': st_account, 'gas': GAS_LIMIT})
            self.voting_balances[st_account] = {
                    'value': st_value,
                    'unlock_time': tx.events['Deposit']['locktime']
            }

    def rule_increase_amount(self, st_account, st_value):
        if st_value == 0:
            with brownie.reverts("dev: need non-zero value"):
                self.voting_escrow.increase_amount(st_value, {'from': st_account, 'gas': GAS_LIMIT})

        elif self.voting_balances[st_account]['value'] == 0:
            with brownie.reverts("No existing lock found"):
                self.voting_escrow.increase_amount(st_value, {'from': st_account, 'gas': GAS_LIMIT})

        elif self.voting_balances[st_account]['unlock_time'] <= chain.time():
            with brownie.reverts("Cannot add to expired lock. Withdraw"):
                self.voting_escrow.increase_amount(st_value, {'from': st_account, 'gas': GAS_LIMIT})

        else:
            self.voting_escrow.increase_amount(st_value, {'from': st_account, 'gas': GAS_LIMIT})
            self.voting_balances[st_account]['value'] += st_value

    def rule_increase_unlock_time(self, st_account, st_lock_duration):
        unlock_time = (chain.time() + st_lock_duration * WEEK) // WEEK * WEEK

        if self.voting_balances[st_account]['unlock_time'] <= chain.time():
            with brownie.reverts("Lock expired"):
                self.voting_escrow.increase_unlock_time(unlock_time, {'from': st_account, 'gas': GAS_LIMIT})

        elif self.voting_balances[st_account]['value'] == 0:
            with brownie.reverts("Nothing is locked"):
                self.voting_escrow.increase_unlock_time(unlock_time, {'from': st_account, 'gas': GAS_LIMIT})

        elif unlock_time <= self.voting_balances[st_account]['unlock_time']:
            with brownie.reverts("Can only increase lock duration"):
                self.voting_escrow.increase_unlock_time(unlock_time, {'from': st_account, 'gas': GAS_LIMIT})

        elif unlock_time > chain.time() + 86400 * 365 * 4:
            with brownie.reverts("Voting lock can be 4 years max"):
                self.voting_escrow.increase_unlock_time(unlock_time, {'from': st_account, 'gas': GAS_LIMIT})

        else:
            tx = self.voting_escrow.increase_unlock_time(unlock_time, {'from': st_account, 'gas': GAS_LIMIT})
            self.voting_balances[st_account]['unlock_time'] = tx.events['Deposit']['locktime']

    def rule_withdraw(self, st_account):
        """
        Withdraw tokens from the voting escrow.
        """
        if self.voting_balances[st_account]['unlock_time'] > chain.time():
            # fail path - before unlock time
            with brownie.reverts("The lock didn't expire"):
                self.voting_escrow.withdraw({'from': st_account, 'gas': GAS_LIMIT})

        else:
            # success path - specific amount
            self.voting_escrow.withdraw({'from': st_account, 'gas': GAS_LIMIT})
            self.voting_balances[st_account]['value'] = 0

    def rule_checkpoint(self, st_account):
        self.voting_escrow.checkpoint({'from': st_account, 'gas': GAS_LIMIT})

    def rule_advance_time(self, st_sleep_duration):
        """
        Advance the clock.
        """
        chain.sleep(st_sleep_duration * WEEK)

        # check the balance as a transaction, to ensure a block is mined after time travel
        self.token.balanceOf.transact(self.accounts[0], {'from': self.accounts[0]})

    def invariant_token_balances(self):
        """
        Verify that token balances are correct.
        """
        for acct in self.accounts:
            assert self.token.balanceOf(acct) == 10**40 - self.voting_balances[acct]['value']

    def invariant_escrow_current_balances(self):
        """
        Verify the sum of all escrow balances is equal to the escrow totalSupply.
        """
        total_supply = 0
        timestamp = chain[-1].timestamp

        for acct in self.accounts:
            data = self.voting_balances[acct]

            balance = self.voting_escrow.balanceOf(acct)
            total_supply += balance

            if data['unlock_time'] > timestamp and data['value'] // MAX_TIME > 0:
                assert balance
            elif not data['value'] or data['unlock_time'] <= timestamp:
                assert not balance

        assert self.voting_escrow.totalSupply() == total_supply

    def invariant_historic_balances(self):
        """
        Verify the sum of historic escrow balances is equal to the historic totalSupply.
        """
        total_supply = 0
        block_number = history[-4].block_number

        for acct in self.accounts:
            total_supply += self.voting_escrow.balanceOfAt(acct, block_number)

        assert self.voting_escrow.totalSupplyAt(block_number) == total_supply


def test_state_machine(state_machine, accounts, ERC20, VotingEscrow):
    token = ERC20.deploy("", "", 18, {'from': accounts[0]})
    voting_escrow = VotingEscrow.deploy(
        token, 'Voting-escrowed CRV', 'veCRV', 'veCRV_0.99', {'from': accounts[0]}
    )

    state_machine(StateMachine, accounts, token, voting_escrow)
