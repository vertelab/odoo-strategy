---
name: unit-economics
description: Calculate unit economics (CAC, LTV, payback period) from Odoo sales and marketing data.
  Triggers: "unit economics", "CAC", "LTV", "customer acquisition cost",
  "lifetime value", "payback period", "unit cost".
metadata:
  version: 1.0.0
---

# Unit Economics

Calculate CAC, LTV, and payback period from Odoo data.

## Data Sources

- `sale.order`: revenue per customer (LTV basis)
- `res.partner`: customer count
- `crm.lead`: acquisition source and cost
- `account.move.line`: marketing expenses (CAC basis)

## Key Metrics

1. **CAC (Customer Acquisition Cost)**
   - Total marketing + sales cost / new customers acquired
   
2. **LTV (Lifetime Value)**
   - Average revenue per customer × average customer lifetime
   - Or: ARPU / churn rate

3. **LTV:CAC Ratio**
   - Target: > 3:1 for healthy SaaS

4. **Payback Period**
   - CAC / monthly gross margin per customer
   - Target: < 12 months

## Process
1. Sum marketing/sales costs from account data
2. Count new customers in period
3. Calculate average revenue per customer
4. Estimate churn rate from inactive customers
5. Compute all metrics
6. Flag if LTV:CAC < 3 or payback > 18 months
