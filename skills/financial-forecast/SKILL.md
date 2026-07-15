---
name: financial-forecast
description: Generate financial forecasts from BMC data with scenario modeling.
  Triggers: "financial forecast", "revenue projection", "break-even",
  "what-if scenario", "financial model", "cash flow forecast".
metadata:
  version: 1.0.0
---

# Financial Forecast

Generate financial forecasts and what-if scenarios from BMC data.

## Data Sources

- `business.model.canvas`: revenue_streams, cost_structure
- `sale.order`: historical revenue for validation
- `account.move.line`: historical costs for validation
- `strategy.forecast`: existing forecasts
- `strategy.scenario`: existing scenarios

## Forecast Generation

1. **Baseline**: From BMC data → monthly revenue/cost projections for 12-36 months
2. **Validate**: Compare against historical Sale/Account data
3. **Metrics**: Break-even date, profit margin, revenue growth rate

## Scenario Generation (4-6 scenarios)

1. **Optimistic**: Best realistic case (+20% revenue, -10% costs)
2. **Pessimistic**: Worst realistic case (-20% revenue, +15% costs)
3. **Growth**: Scale 5x over 3 years
4. **Market Shift**: External disruption scenario
5. **Price Change**: ±20% price adjustment
6. **Cost Shock**: Key input cost +30%

## Output
- `strategy.forecast` with monthly forecast lines
- `strategy.scenario` records with adjusted outcomes
- `strategy.risk` records (top 5 strategic risks)
- `strategy.action` records per scenario
