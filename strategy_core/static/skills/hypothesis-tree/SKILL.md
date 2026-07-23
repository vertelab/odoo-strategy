---
name: hypothesis-tree
description: Build and test strategic hypotheses using Odoo CRM and sales data.
  Triggers: "hypothesis tree", "hypothesis driven", "test assumption",
  "validate hypothesis", "what if analysis".
metadata:
  version: 1.0.0
---

# Hypothesis Tree

Build and validate strategic hypotheses against Odoo data.

## Data Sources

- `crm.lead`: test hypotheses against pipeline outcomes
- `sale.order`: validate revenue assumptions
- `account.move.line`: validate cost assumptions
- `business.model.canvas`: strategic hypotheses to test

## Structure

1. **Core hypothesis**: What do we believe to be true?
2. **Sub-hypotheses**: What must also be true for the core to hold?
3. **Tests**: What Odoo data would confirm or refute each?
4. **Evidence**: Actual data findings with confidence level

## Process

1. State the core strategic hypothesis
2. Decompose into 3-5 sub-hypotheses
3. For each: identify the Odoo query that would test it
4. Run the queries against live data
5. Label evidence: [F]act, [I]nference, [A]ssumption, [E]stimate
6. Update hypothesis confidence: Confirmed / Likely / Unclear / Refuted
7. Recommend action based on findings

## Example

Hypothesis: "We should enter the German market"
- Sub: "German customers have the same needs as Swedish" → test: CRM lead similarity
- Sub: "We can serve in German with current team" → test: HR language skills
- Sub: "German CAC is ≤ 1.5× Swedish" → test: market research + pilot
