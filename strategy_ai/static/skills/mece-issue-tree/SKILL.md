---
name: mece-issue-tree
description: Structure business problems using MECE (Mutually Exclusive, Collectively Exhaustive) issue trees.
  Triggers: "MECE", "issue tree", "problem structuring", "mutually exclusive",
  "collectively exhaustive", "break down problem".
metadata:
  version: 1.0.0
---

# MECE Issue Tree

Decompose complex business problems into MECE components.

## Principle

MECE = Mutually Exclusive, Collectively Exhaustive
- No overlap between branches (ME)
- All possibilities covered (CE)

## Data Sources

- `business.model.canvas`: strategic context
- `crm.lead`: problem signals from pipeline
- `strategy.risk`: identified risks to decompose

## Process

1. **Define the problem**: State the core question precisely
2. **Identify the first split**: What is the primary dimension?
   - Common splits: internal/external, revenue/cost, product/market, strategic/operational
3. **Decompose each branch**: Apply MECE to each sub-problem
4. **Prioritize branches**: Which sub-problems drive 80% of the outcome?
5. **Formulate hypotheses**: For each prioritized branch, what's the likely answer?
6. **Identify data needed**: What Odoo data would test each hypothesis?

## Example

Problem: "Why is profit declining?"
- Revenue side (ME): price × volume → price down? volume down? mix shift?
- Cost side (ME): fixed costs up? variable costs up? one-time charges?
- Together: CE (all profit drivers covered)
