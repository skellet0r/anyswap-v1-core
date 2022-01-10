def test_fund(alice, anycall):
    tx = anycall.fund(alice, {"from": alice, "value": 10 ** 18})

    assert anycall.funds(alice) == 10 ** 18
    assert tx.events["Fund"].values() == [alice, 10 ** 18]
    assert anycall.balance() == 10 ** 18


def test_fund_alternate_account(alice, bob, anycall):
    anycall.fund(bob, {"from": alice, "value": 10 ** 18})

    assert anycall.funds(alice) == 0
    assert anycall.funds(bob) == 10 ** 18


def test_refund_mpc_full(alice, anycall):
    anycall.anyCall(alice, [], [], [], [], 0, {"from": anycall.mpc(), "gas_price": 10 ** 9})
    expense = anycall.expenses()
    assert expense > 0

    anycall.fund(alice, {"from": alice, "value": expense})
    prev_balance = alice.balance()
    anycall.refundMPC({"from": alice})
    assert alice.balance() == prev_balance + expense


def test_refund_mpc_partial(alice, anycall):
    anycall.anyCall(alice, [], [], [], [], 0, {"from": anycall.mpc(), "gas_price": 10 ** 9})
    expense = anycall.expenses()
    assert expense > 0

    anycall.fund(alice, {"from": alice, "value": expense // 2})
    prev_balance = alice.balance()
    anycall.refundMPC({"from": alice})
    assert alice.balance() == prev_balance + expense // 2
    assert anycall.expenses() == expense - (expense // 2)
