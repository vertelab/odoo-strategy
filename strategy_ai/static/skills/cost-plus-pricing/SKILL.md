---
name: cost-plus-pricing
description: Calculate cost-plus pricing from Odoo product costs and margin targets.
  Triggers: "cost plus pricing", "cost based pricing", "margin pricing",
  "markup", "cost plus margin".
metadata:
  version: 1.0.0
---

# Cost-Plus Pricing

Calculate prices from actual product costs with margin targets.

## Data Sources

- `product.template`: standard_price (cost), list_price (current price)
- `account.move.line`: actual cost components
- `mrp.bom`: bill of materials for manufactured products
- `purchase.order.line`: procurement costs

## Calculation

```
Selling Price = Total Cost × (1 + Markup %)

Total Cost = Direct Materials + Direct Labor + Overhead Allocation
Markup % = Target margin / (1 - Target margin)
```

## Process

1. Calculate total cost per product from BOM + purchase data
2. Apply target margin (industry benchmark or company target)
3. Compare calculated price to current list_price
4. Flag products where current price < cost-plus (margin erosion)
5. Flag products where current price >> cost-plus (pricing opportunity)
6. Segment: high-margin (protect), low-margin (investigate), negative-margin (fix or drop)

## Margin Targets by Product Category

- Commodity products: 10-20%
- Differentiated products: 30-50%
- Premium/niche: 50-100%+
