"""Tools the agents can call.

Every tool is a plain function with a docstring; the CrewAI decorator only
wraps them. That means the same logic is testable without a model in the loop.
"""

from __future__ import annotations

import json

from crewai.tools import tool

from . import db
from .policy import decide


def _connection():
    connection = db.connect()
    db.seed(connection)
    return connection


@tool("lookup_order")
def lookup_order(order_id: str) -> str:
    """Look up an order by id and return its customer, item, amount,
    days since delivery, condition and prior refund count."""
    connection = _connection()
    order = db.get_order(connection, order_id)
    connection.close()

    if order is None:
        return json.dumps({"error": f"No order found for {order_id}"})

    return json.dumps(
        {
            "order_id": order.order_id,
            "customer": order.customer,
            "item": order.item,
            "amount": order.amount,
            "delivered_days_ago": order.delivered_days_ago,
            "condition": order.condition,
            "prior_refunds": order.prior_refunds,
        }
    )


@tool("check_refund_policy")
def check_refund_policy(order_id: str, reason: str) -> str:
    """Apply the refund policy to an order and return the decision
    (refund, replace or escalate) with the rules and citations that fired."""
    connection = _connection()
    order = db.get_order(connection, order_id)
    connection.close()

    if order is None:
        return json.dumps({"error": f"No order found for {order_id}"})

    decision = decide(order, reason)
    return json.dumps(
        {
            "order_id": order.order_id,
            "action": decision.action,
            "needs_human": decision.needs_human,
            "reasons": decision.reasons,
            "citations": decision.citations,
        }
    )


@tool("escalate_ticket")
def escalate_ticket(order_id: str, summary: str) -> str:
    """Create an escalation payload for a human reviewer. Use when the policy
    returns escalate, or when the request falls outside the documented rules."""
    return json.dumps(
        {
            "ticket": f"ESC-{order_id}",
            "order_id": order_id,
            "summary": summary,
            "queue": "human-review",
            "status": "open",
        }
    )
