---
name: root-cause-analysis
description: Find root causes of business problems using 5 Whys and Fishbone diagrams.
  Triggers: "root cause", "5 whys", "fishbone", "Ishikawa", "why is this happening",
  "cause analysis".
metadata:
  version: 1.0.0
---

# Root Cause Analysis

Find the root cause of business problems using structured methods.

## Data Sources

- `strategy.risk`: identified risks to analyze
- `crm.lead`: lost deals → why?
- `sale.order`: declining segments → why?
- `account.move.line`: cost anomalies → why?
- `project.task`: support issues → why?

## Methods

### 5 Whys
1. State the problem
2. Ask "Why?" → answer
3. Repeat 4 more times
4. Root cause found when you reach a process/system failure

### Fishbone (Ishikawa)
Categories: People, Process, Technology, Materials, Environment, Measurement

## Process

1. Define the problem precisely with measurable impact
2. Apply 5 Whys to trace from symptom to root cause
3. Cross-check with Fishbone to ensure all categories considered
4. Validate root cause against Odoo data
5. Propose corrective action
6. Store as `strategy.risk` or link to existing risk

## Example

Problem: "Q3 revenue down 15%"
- Why? → Customer churn increased 3×
- Why? → Support response time doubled
- Why? → Key support person left
- Why? → No backup/ documentation
- Why? → No succession planning process
→ Root cause: Process failure in HR succession planning
