import brownie
from brownie import ZERO_ADDRESS


def test_change_mpc_success(alice, bob, anycall):
    tx = anycall.changeMPC(bob, {"from": alice})
    expected_timestamp = tx.timestamp + 86400 * 2

    assert anycall.mpc() == alice
    assert anycall.pendingMPC() == bob
    assert anycall.delayMPC() == expected_timestamp
    assert tx.events["LogChangeMPC"].values() == [alice, bob, expected_timestamp]


def test_change_mpc_non_zero_address(alice, anycall):
    with brownie.reverts("MPC: mpc is the zero address"):
        anycall.changeMPC(ZERO_ADDRESS, {"from": alice})


def test_change_mpc_only_active_mpc(bob, anycall):
    with brownie.reverts("MPC: only mpc"):
        anycall.changeMPC(bob, {"from": bob})


def test_apply_mpc_success(alice, bob, chain, anycall):
    anycall.changeMPC(bob, {"from": alice})
    chain.mine(timestamp=anycall.delayMPC())  # fast forward
    tx = anycall.applyMPC({"from": bob})

    assert anycall.mpc() == bob
    assert anycall.pendingMPC() == ZERO_ADDRESS
    assert anycall.delayMPC() == 0
    assert tx.events["LogApplyMPC"].values() == [alice, bob, tx.timestamp]


def test_apply_mpc_only_after_delay(alice, bob, chain, anycall):
    anycall.changeMPC(bob, {"from": alice})
    chain.mine(timestamp=anycall.delayMPC() - 60)  # fast forward
    with brownie.reverts("MPC: time before delayMPC"):
        anycall.applyMPC({"from": bob})


def test_apply_mpc_only_pending_mpc(alice, bob, chain, anycall):
    anycall.changeMPC(bob, {"from": alice})
    chain.mine(timestamp=anycall.delayMPC())  # fast forward
    with brownie.reverts("MPC: only pendingMPC"):
        anycall.applyMPC({"from": alice})
