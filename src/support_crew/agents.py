"""CrewAI agents and tasks.

Three roles, one job each:
  intake    -> reads the order
  policy    -> applies the rule engine and cites the clauses
  resolution-> writes the customer reply, or escalates

The crew needs an LLM. Without a configured model, use the deterministic CLI
path (`python -m support_crew.cli --order-id ORD-1001 --reason damaged`), which
exercises the same policy engine and tools.
"""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from .tools import check_refund_policy, escalate_ticket, lookup_order

intake_analyst = Agent(
    role="Intake Analyst",
    goal="Read the order and restate the customer's request in one precise line.",
    backstory=(
        "You handle the first pass of every support ticket. You never guess: if "
        "the order id is missing or unknown, you say so and stop."
    ),
    tools=[lookup_order],
    verbose=False,
    allow_delegation=False,
)

policy_reviewer = Agent(
    role="Policy Reviewer",
    goal="Apply the refund policy and report the decision with its citations.",
    backstory=(
        "You are the compliance check. You call the policy tool for every case "
        "and quote the rule ids it returns. You do not invent policy."
    ),
    tools=[check_refund_policy],
    verbose=False,
    allow_delegation=False,
)

resolution_writer = Agent(
    role="Resolution Writer",
    goal="Write a short customer reply and escalate anything that needs a human.",
    backstory=(
        "You write the message the customer actually reads: two or three "
        "sentences, plain language, no promises the policy did not authorise."
    ),
    tools=[escalate_ticket],
    verbose=False,
    allow_delegation=False,
)


def build_crew() -> Crew:
    intake_task = Task(
        description=(
            "Look up order {order_id} and summarise: customer, item, amount, "
            "days since delivery, condition, prior refunds. State the reason "
            "the customer gave: {reason}."
        ),
        expected_output="A one-paragraph summary of the order and the request.",
        agent=intake_analyst,
    )

    policy_task = Task(
        description=(
            "Call check_refund_policy for {order_id} with reason '{reason}'. "
            "Report the action, whether it needs a human, and every citation."
        ),
        expected_output=(
            "The action (refund, replace or escalate), the human-review flag, "
            "the reasons and the rule citations."
        ),
        agent=policy_reviewer,
        context=[intake_task],
    )

    resolution_task = Task(
        description=(
            "Using the policy result, write the customer reply. If the decision "
            "is escalate, call escalate_ticket first and tell the customer their "
            "case has been passed to a specialist."
        ),
        expected_output="A short customer-facing reply plus the escalation id if any.",
        agent=resolution_writer,
        context=[intake_task, policy_task],
    )

    return Crew(
        agents=[intake_analyst, policy_reviewer, resolution_writer],
        tasks=[intake_task, policy_task, resolution_task],
        process=Process.sequential,
        verbose=False,
    )
