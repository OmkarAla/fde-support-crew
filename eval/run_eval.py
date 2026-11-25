"""Deterministic evaluation of the decision layer.

Runs every golden case through the policy engine and fails if the action or the
expected citation differs. This is the part of the system that must be exact;
the agents are evaluated separately and manually against the same cases.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from support_crew import db  # noqa: E402
from support_crew.policy import decide  # noqa: E402


def main() -> int:
    cases = json.loads((ROOT / "eval" / "golden.json").read_text())
    connection = db.connect()
    db.seed(connection)

    failures = 0
    print(f"{'order':<10} {'expected':<10} {'actual':<10} result")
    print("-" * 48)

    for case in cases:
        order = db.get_order(connection, case["order_id"])
        if order is None:
            print(f"{case['order_id']:<10} missing order")
            failures += 1
            continue

        decision = decide(order, case["reason"])
        expected = case["expect"]
        ok = (
            decision.action == expected["action"]
            and expected["citation"] in decision.citations
        )
        failures += 0 if ok else 1
        print(
            f"{case['order_id']:<10} {expected['action']:<10} "
            f"{decision.action:<10} {'PASS' if ok else 'FAIL'}"
        )

    connection.close()
    print(f"\n{len(cases) - failures}/{len(cases)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
