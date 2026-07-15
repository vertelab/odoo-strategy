---
name: okr-framework
description: Generate Objectives and Key Results from strategy data.
  Triggers: "OKR", "objectives and key results", "goal setting", "strategic objectives".
metadata:
  version: 1.0.0
---

# OKR Framework

Generate OKRs (Objectives & Key Results) from business strategy.

## Data Sources

- `business.model.canvas`: strategic direction
- `swot.analysis`: strengths to leverage, weaknesses to address
- `sale.order`: revenue baselines for targets
- `strategy.risk`: risks to mitigate

## Structure

- **Objective**: Qualitative, inspirational, time-bound (quarter)
- **Key Results** (3-5 per objective): Quantitative, measurable, outcome-focused

## OKR Types

1. **Committed OKRs** — must achieve 100% (operational)
2. **Aspirational OKRs** — stretch goals (60-70% is success)

## Process
1. Read BMC + SWOT for strategic context
2. Draft 3-5 quarterly objectives aligned to strategy
3. For each objective, define 3-5 measurable key results
4. Set baseline values from current Odoo data
5. Store as `okr.objective` with `okr.key.result` records
