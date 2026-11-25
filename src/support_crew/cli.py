"""Command line entry point.

Two modes:
  --order-id ...          deterministic policy decision (no model, always works)
  --order-id ... --crew   run the three-agent CrewAI flow (needs a model key)
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from . import db
from .policy import decide


def _deterministic(order_id: str, reason: str) -> int:
    connection = db.connect()
    db.seed(connection)
    order = db.get_order(connection, order_id)
    connection.close()

    if order is None:
        print(json.dumps({"error": f"No order found for {order_id}"}))
        return 2

    decision = decide(order, reason)
    print(
        json.dumps(
            {
                "order_id": order.order_id,
                "action": decision.action,
                "needs_human": decision.needs_human,
                "reasons": decision.reasons,
                "citations": decision.citations,
            },
            indent=2,
        )
    )
    return 0


def _crew(order_id: str, reason: str) -> int:
    if not any(os.environ.get(key) for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")):
        print(
            "Crew mode needs a model key (OPENAI_API_KEY or ANTHROPIC_API_KEY). "
            "Run without --crew for the deterministic path.",
            file=sys.stderr,
        )
        return 3

    from .agents import build_crew

    crew = build_crew()
    result = crew.kickoff(inputs={"order_id": order_id, "reason": reason})
    print(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Support triage crew")
    parser.add_argument("--order-id", required=True)
    parser.add_argument("--reason", default="customer request")
    parser.add_argument("--crew", action="store_true", help="run the agents")
    args = parser.parse_args(argv)

    if args.crew:
        return _crew(args.order_id, args.reason)
    return _deterministic(args.order_id, args.reason)


if __name__ == "__main__":
    raise SystemExit(main())
