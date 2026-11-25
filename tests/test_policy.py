from support_crew.policy import (
    MANUAL_APPROVAL_LIMIT,
    RETURN_WINDOW_DAYS,
    Order,
    decide,
)


def make_order(**overrides) -> Order:
    values = {
        "order_id": "ORD-TEST",
        "customer": "Test Customer",
        "item": "Keyboard",
        "amount": 100.0,
        "delivered_days_ago": 5,
        "condition": "unused",
        "prior_refunds": 0,
    }
    values.update(overrides)
    return Order(**values)


def test_eligible_order_is_refunded():
    decision = decide(make_order(), "changed my mind")

    assert decision.action == "refund"
    assert decision.citations == ["policy:refunds.eligible"]
    assert decision.needs_human is False


def test_damaged_item_is_replaced():
    decision = decide(make_order(condition="damaged"), "arrived cracked")

    assert decision.action == "replace"
    assert "policy:replace.damaged" in decision.citations


def test_outside_window_escalates():
    decision = decide(make_order(delivered_days_ago=RETURN_WINDOW_DAYS + 1), "late return")

    assert decision.action == "escalate"
    assert "policy:returns.window" in decision.citations


def test_high_value_escalates_for_approval():
    decision = decide(make_order(amount=MANUAL_APPROVAL_LIMIT + 0.01), "too expensive")

    assert decision.action == "escalate"
    assert "policy:refunds.limit" in decision.citations


def test_used_item_escalates():
    decision = decide(make_order(condition="used"), "not as described")

    assert decision.action == "escalate"
    assert "policy:returns.condition" in decision.citations


def test_repeat_refunder_escalates_before_condition():
    decision = decide(make_order(condition="used", prior_refunds=3), "again")

    assert decision.action == "escalate"
    assert decision.citations == ["policy:risk.repeat_refunds"]
