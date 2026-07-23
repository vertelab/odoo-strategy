---
name: freemium-packaging
description: Analyze freemium and packaging strategies from Odoo sales and product data.
  Triggers: "freemium", "packaging", "product tiers", "free to paid",
  "conversion rate", "product mix", "bundling".
metadata:
  version: 1.0.0
---

# Freemium & Packaging Strategy

Optimize product tiers and freemium conversion.

## Data Sources

- `product.template`: product catalog and tiers
- `sale.order`: product mix, upgrade patterns
- `res.partner`: customer segments and upgrade behavior
- `crm.lead`: feature requests and objections

## Analysis

1. **Product Mix**: what % of customers are on each tier?
2. **Upgrade Path**: which tier do customers upgrade from/to?
3. **Conversion Rate**: free → paid %, paid → premium %
4. **Feature Gating**: which features drive upgrades?
5. **ARPU by Tier**: revenue per user per tier

## Freemium Models

- **Feature-limited**: free = basic features, paid = advanced
- **Usage-limited**: free = X per month, paid = unlimited
- **Time-limited**: free = 14-day trial, paid = ongoing
- **Seat-limited**: free = 1 user, paid = team

## Process

1. Map current product tiers and features from product.template
2. Analyze upgrade patterns from sale.order history
3. Calculate conversion rates per tier
4. Identify conversion bottlenecks (tier where users get stuck)
5. Recommend packaging changes: what to gate, what to bundle
6. Estimate revenue impact of packaging changes
