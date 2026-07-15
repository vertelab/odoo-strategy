---
name: porters-five-forces
description: Apply Porter's Five Forces to analyze industry competitiveness.
  Triggers: "Porter", "five forces", "competitive forces", "industry analysis",
  "competitive rivalry", "barriers to entry".
metadata:
  version: 1.0.0
---

# Porter's Five Forces

Analyze competitive intensity and industry attractiveness.

## Data Sources

- `social_marketing.competitor`: competitor data
- `crm.lead`: win/loss reasons → competitive dynamics
- `res.partner`: supplier and buyer concentration
- `product.template`: substitution risk

## Five Forces

1. **Threat of New Entry** — how easy is it to enter?
   - Economies of scale, capital requirements, access to distribution
2. **Bargaining Power of Suppliers** — can suppliers push prices up?
   - Supplier concentration, switching costs, substitute inputs
3. **Bargaining Power of Buyers** — can buyers push prices down?
   - Buyer concentration, price sensitivity, switching costs
4. **Threat of Substitutes** — can customers use alternatives?
   - Relative price/performance, switching costs
5. **Competitive Rivalry** — how intense is competition?
   - Number of competitors, industry growth, exit barriers

## Process
1. Analyze each force using CRM + competitor data
2. Rate each force: Low / Medium / High
3. Identify the dominant force shaping industry profitability
4. Recommend strategic response to the strongest forces
