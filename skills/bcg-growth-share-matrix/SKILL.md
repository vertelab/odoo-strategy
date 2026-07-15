---
name: bcg-growth-share-matrix
description: Apply the BCG Growth-Share Matrix to analyze product portfolio from Odoo sales data.
  Triggers: "BCG matrix", "growth share", "stars cash cows", "product portfolio",
  "Boston matrix", "portfolio analysis".
metadata:
  version: 1.0.0
---

# BCG Growth-Share Matrix

Plot products on the BCG matrix using actual Odoo sales data.

## Data Sources

- `sale.order`: revenue and growth per product
- `product.template`: product catalog
- Market growth from CRM pipeline trends

## 4 Quadrants

1. **Stars** (high growth, high share)
   - Invest heavily — future cash cows
   
2. **Cash Cows** (low growth, high share)
   - Milk for profit — fund stars and question marks

3. **Question Marks** (high growth, low share)
   - Invest selectively or divest

4. **Dogs** (low growth, low share)
   - Divest or harvest

## Process
1. Calculate relative market share and growth rate per product from Sale data
2. Plot each product on the 2×2 matrix
3. Size bubbles by revenue contribution
4. Recommend actions per quadrant:
   - Stars → increase investment
   - Cash Cows → maintain, extract profit
   - Question Marks → selective investment or exit
   - Dogs → divest or reposition
