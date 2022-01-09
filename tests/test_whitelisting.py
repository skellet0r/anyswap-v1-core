import itertools as it
from collections import defaultdict

import brownie
from brownie import accounts
from brownie.test import strategy


class StateMachine:

    st_address = strategy("address")
    st_bool = strategy("bool")
    st_uint = strategy("uint256", min_value=1, max_value=16)

    def __init__(cls, anycall):
        cls.anycall = anycall

    def setup(self):
        self.blacklist = defaultdict(bool)
        self.whitelist = defaultdict(lambda: defaultdict(lambda: defaultdict(bool)))

        self.chain_ids = set()

    def rule_blacklist(self, st_address, st_bool):
        self.blacklist[st_address] = st_bool
        self.anycall.blacklist(st_address, st_bool, {"from": self.anycall.mpc()})

    def rule_whitelist(
        self, _from="st_address", _chain_id="st_uint", _to="st_address", _flag="st_bool"
    ):
        self.chain_ids.add(_chain_id)
        if self.whitelist[_from][_chain_id][_to] == _flag:
            with brownie.reverts("nothing change"):
                self.anycall.whitelist(_from, _chain_id, _to, _flag, {"from": self.anycall.mpc()})
        else:
            self.anycall.whitelist(_from, _chain_id, _to, _flag, {"from": self.anycall.mpc()})
            self.whitelist[_from][_chain_id][_to] = _flag

    def invariant(self):
        for account in accounts:
            assert self.blacklist[account] == self.anycall.isBlacklisted(account)

        for account, chain_id in it.product(accounts, self.chain_ids):
            whitelist = {
                self.anycall.whitelists(account, chain_id, i)
                for i in range(self.anycall.whitelistLength(account, chain_id))
            }
            local_whitelist = {k for k, v in self.whitelist[account][chain_id].items() if v is True}
            assert whitelist == local_whitelist

        for _from, _chain_ids in self.whitelist.items():
            for _chain_id, _tos in _chain_ids.items():
                for _to, _value in _tos.items():
                    assert self.anycall.isInWhitelist(_from, _chain_id, _to) == _value


def test_stateful(state_machine, anycall):
    state_machine(StateMachine, anycall)
