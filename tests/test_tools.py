import json

from support_crew.tools import check_refund_policy, lookup_order


def test_lookup_returns_the_order():
    payload = json.loads(lookup_order.run("ORD-1001"))

    assert payload["order_id"] == "ORD-1001"
    assert payload["customer"] == "Asha Rao"
    assert payload["amount"] == 129.0


def test_lookup_reports_unknown_order():
    payload = json.loads(lookup_order.run("ORD-9999"))

    assert "error" in payload


def test_policy_tool_returns_action_and_citations():
    payload = json.loads(check_refund_policy.run("ORD-1002", "arrived damaged"))

    assert payload["action"] == "replace"
    assert payload["needs_human"] is False
    assert "policy:replace.damaged" in payload["citations"]


def test_policy_tool_escalates_large_order():
    payload = json.loads(check_refund_policy.run("ORD-1003", "changed my mind"))

    assert payload["action"] == "escalate"
    assert payload["needs_human"] is True
