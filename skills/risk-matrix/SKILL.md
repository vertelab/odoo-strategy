---
name: risk-matrix
description: Map strategic risks on probability × impact matrix using strategy.risk data.
  Triggers: "risk matrix", "risk assessment", "probability impact",
  "risk heatmap", "strategic risks".
metadata:
  version: 1.0.0
---

# Risk Matrix

Map and prioritize strategic risks using probability × impact.

## Data Sources

- `strategy.risk`: existing identified risks with probability and impact
- `business.model.canvas`: strategic context
- `strategy.forecast`: financial risks

## Structure

```
Impact
  ↑
Critical │  Monitor     │  Mitigate    │  ACT NOW     │
High     │  Monitor     │  Mitigate    │  Mitigate    │
Medium   │  Accept      │  Monitor     │  Mitigate    │
Low      │  Accept      │  Accept      │  Monitor     │
         └──────────────┴──────────────┴──────────────→ Probability
            Low            Medium         High/Critical
```

## Process

1. List all `strategy.risk` records for the business
2. Classify each by probability (low/medium/high/critical)
3. Classify each by impact amount (monetary)
4. Plot on 2×2 or 3×3 matrix
5. For "ACT NOW" quadrant: generate immediate `strategy.action` records
6. For "Mitigate" quadrant: schedule mitigation actions
7. For "Monitor": set review dates
8. For "Accept": document acceptance rationale
