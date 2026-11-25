"""Deterministic refund/replacement policy.

The agents reason and write the customer reply; this module owns the decision.
That split is deliberate: an LLM can misread a date or a threshold, a pure
function cannot, and every decision here is testable without a model call.
"""

from __future__ import annotations

from dataclasses import dataclass, field

RETURN_WINDOW_DAYS = 30
MANUAL_APPROVAL_LIMIT = 500.00
MAX_PRIOR_REFUNDS = 3


@dataclass(frozen=True)
class Order:
    order_id: str
    customer: str
    item: str
    amount: float
    delivered_days_ago: int
    condition: str
    prior_refunds: int = 0


@dataclass(frozen=True)
class Decision:
    action: str
    reasons: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)

    @property
    def needs_human(self) -> bool:
        return self.action == "escalate"


def decide(order: Order, reason: str) -> Decision:
    """Return refund / replace / escalate with the rules that fired."""
    reasons: list[str] = []
    citations: list[str] = []

    if order.delivered_days_ago > RETURN_WINDOW_DAYS:
        reasons.append(
            f"Delivered {order.delivered_days_ago} days ago, outside the "
            f"{RETURN_WINDOW_DAYS}-day return window"
        )
        citations.append("policy:returns.window")
        return Decision("escalate", reasons, citations)

    if order.prior_refunds >= MAX_PRIOR_REFUNDS:
        reasons.append(
            f"{order.prior_refunds} prior refunds on this account; needs manual review"
        )
        citations.append("policy:risk.repeat_refunds")
        return Decision("escalate", reasons, citations)

    if order.condition == "used":
        reasons.append("Item condition is 'used', which is outside the refund policy")
        citations.append("policy:returns.condition")
        return Decision("escalate", reasons, citations)

    if order.amount > MANUAL_APPROVAL_LIMIT:
        reasons.append(
            f"Amount {order.amount:.2f} exceeds the {MANUAL_APPROVAL_LIMIT:.2f} "
            "automatic-refund limit"
        )
        citations.append("policy:refunds.limit")
        return Decision("escalate", reasons, citations)

    if order.condition == "damaged":
        reasons.append("Item arrived damaged within the return window")
        citations.append("policy:replace.damaged")
        return Decision("replace", reasons, citations)

    reasons.append(f"Within the return window and eligible under '{reason}'")
    citations.append("policy:refunds.eligible")
    return Decision("refund", reasons, citations)
