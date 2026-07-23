---
name: value-based-pricing
description: Recommend value-based pricing using Odoo sales history and customer segments.
  Triggers: "value based pricing", "pricing strategy", "willingness to pay",
  "price optimization", "what should we charge".
metadata:
  version: 1.0.0
---

# Value-Based Pricing

Set prices based on customer-perceived value, not cost.

## Data Sources

- `sale.order`: historical pricing and conversion
- `product.template`: current prices and costs
- `res.partner`: customer segments and willingness-to-pay signals
- `crm.lead`: win/loss reasons related to price

## Analysis

1. **Price sensitivity by segment**: analyze sale.order conversion rate vs price
2. **Feature value**: which features correlate with higher willingness to pay?
3. **Competitor benchmarking**: how do prices compare to competitor data?
4. **Price elasticity**: if price ↑10%, how does volume change?

## Process

1. Segment customers by industry, size, geography
2. Calculate average price paid per segment from sale.order
3. Analyze win/loss rates at different price points
4. Identify value drivers (features that correlate with premium pricing)
5. Recommend optimal price point per segment
6. Estimate revenue impact of price changes

## Pricing Strategies to Evaluate

- **Good-Better-Best**: 3-tier with anchor pricing
- **Per-value-metric**: price per user, per transaction, per usage
- **Segment-specific**: different prices for different industries
