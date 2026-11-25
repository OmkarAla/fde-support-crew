# Case study — Support Triage Crew

**One line:** a three-agent support system where the model writes the reply and the code makes the refund decision.

## The problem

Support teams want agents to triage tickets, but refunds and replacements are policy decisions with money attached. A pure-LLM agent is fluent and unreliable: it will refund a 44-day-old order because the customer asked nicely. The useful shape is narrower — let the model read, route and write, and let deterministic code decide.

## My role

Solo. Designed the policy model, the tool contracts, the crew, the evaluation set and the tests.

## Two choices worth defending

**1. Deterministic policy core under the agents.**
`policy.decide(order, reason)` returns `refund`, `replace` or `escalate` plus the rule ids that fired. The `check_refund_policy` tool is a thin wrapper. The alternative — putting the rules in the agent's prompt — reads better in a demo and fails the first time a customer argues. This is the same reasoning as a rules engine behind an LLM: the model gets to be helpful, not authoritative.

**2. Sequential crew, three narrow roles.**
Intake reads the order, policy applies the rules, resolution writes the reply. I rejected a hierarchical crew with a manager agent because there is nothing to plan: the workflow is fixed and sequential, and a manager would add tokens and variance without adding decisions. Narrow roles also make failures legible — if the reply is wrong but the decision is right, the bug is in the writer, not the policy.

## How I measured it

- **6 policy tests** covering every branch, including the ordering bug where a repeat refunder with a used item must escalate on `risk.repeat_refunds` before `returns.condition`.
- **4 tool tests**, including the unknown-order path.
- **5 golden eval cases** (`eval/golden.json`) with expected action and citation; `run_eval.py` fails the build if either changes.
- **Crew behaviour** is verified manually against the same five cases, because model output is not byte-stable.

That split matters: the part that must be exact is automated; the part that is generative is reviewed.

## What I'd do differently

- **Retrieval over the actual policy document** instead of rule ids, so the customer reply can quote the clause.
- **An LLM-as-judge eval** for the written reply: does it promise only what the decision authorised, and does it cite correctly? Right now that's a human read.
- **Tracing and cost per ticket** (OpenTelemetry or Langfuse) before calling it production-ready.
- **Human-in-the-loop UI** rather than a JSON escalation payload — the approval needs to be one click, with the full context visible.
