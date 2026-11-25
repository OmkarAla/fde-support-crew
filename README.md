# Support Triage Crew

A three-agent CrewAI system for customer support, built around one rule: **the model writes the reply, the code makes the decision.**

An LLM can misread a date or a refund threshold. So the policy lives in a pure Python function with citations, the agents orchestrate around it, and every decision is reproducible and testable without a model call.

## Why it's built this way

| Layer | Owns | Why |
|---|---|---|
| Policy engine (`policy.py`) | refund / replace / escalate | Deterministic, unit-tested, no token cost |
| Tools (`tools.py`) | order lookup, policy check, escalation | Plain functions; the agent only decides when to call them |
| Crew (`agents.py`) | intake → policy → resolution | Each agent has one job and an explicit hand-off |
| Eval (`eval/`) | 5 golden cases | A change that breaks a decision fails the run |

This is the pattern I'd deploy for an enterprise customer: the agent's freedom is in the wording and the routing, not in whether a refund is allowed.

## Rules

| Condition | Action | Citation |
|---|---|---|
| Delivered more than 30 days ago | escalate | `policy:returns.window` |
| 3+ prior refunds on the account | escalate | `policy:risk.repeat_refunds` |
| Condition `used` | escalate | `policy:returns.condition` |
| Amount above 500.00 | escalate | `policy:refunds.limit` |
| Damaged within the window | replace | `policy:replace.damaged` |
| Otherwise | refund | `policy:refunds.eligible` |

## Run it

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows
pip install -e ".[dev]"

# deterministic decision, no model needed
support-crew --order-id ORD-1002 --reason "arrived cracked"

# full agent flow (needs OPENAI_API_KEY or ANTHROPIC_API_KEY)
support-crew --order-id ORD-1002 --reason "arrived cracked" --crew
```

## Test and evaluate

```bash
pytest -q
python eval/run_eval.py
```

`pytest` covers the policy rules and the tools without a model. `run_eval.py` replays the five golden cases and fails if an action or citation changes.

## Limitations

- Five orders in a seeded SQLite database; this is a demonstration, not a production store.
- The crew needs a hosted model key; the deterministic path is the default for that reason.
- No retrieval over policy documents yet — citations are rule ids, not quoted text.
- Escalation writes a JSON payload; there is no ticketing integration.
