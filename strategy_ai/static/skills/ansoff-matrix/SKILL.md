---
name: ansoff-matrix
description: Apply the Ansoff Matrix to identify growth strategies from Odoo data.
  Triggers: "Ansoff", "growth strategy", "market penetration", "diversification",
  "product development", "market development".
metadata:
  version: 1.0.0
---

# Ansoff Matrix

Map growth opportunities across 4 quadrants using live CRM and product data.

## Data Sources

- `crm.lead`: new vs existing markets
- `product.template`: new vs existing products
- `sale.order`: current product-market performance

## 4 Quadrants

1. **Market Penetration** (existing products, existing markets)
   - Increase share in current segments
   - Data: sale.order growth rate in existing segments

2. **Market Development** (existing products, new markets)
   - Enter new geographies or segments
   - Data: crm.lead from new regions/segments

3. **Product Development** (new products, existing markets)
   - Launch new products to current customers
   - Data: product.template gaps vs competitor offerings

4. **Diversification** (new products, new markets)
   - Enter entirely new business areas
   - Data: unexplored product-market combinations

## Process
1. Classify current products and markets from Odoo data
2. Plot on 2×2 matrix
3. Identify highest-potential quadrant based on revenue/probability data
4. Recommend specific growth moves with estimated impact
