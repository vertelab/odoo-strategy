---
name: value-chain-analysis
description: Analyze the value chain from Odoo operational data (MRP, Purchase, Stock, Sale).
  Triggers: "value chain", "value chain analysis", "primary activities",
  "support activities", "Porter value chain".
metadata:
  version: 1.0.0
---

# Value Chain Analysis

Analyze the complete value chain using Odoo process data.

## Data Sources

- `mrp.production`: manufacturing activities
- `purchase.order`: procurement activities
- `stock.picking`: logistics activities
- `sale.order`: sales and distribution
- `crm.lead`: marketing and sales
- `hr.employee`: human resources
- `account.move`: financial management

## Primary Activities

1. **Inbound Logistics** — receiving, storing, distributing inputs
   - Data: `stock.picking` (incoming), `purchase.order`
2. **Operations** — transforming inputs into outputs
   - Data: `mrp.production`
3. **Outbound Logistics** — collecting, storing, distributing to buyers
   - Data: `stock.picking` (outgoing)
4. **Marketing & Sales** — promoting and selling
   - Data: `crm.lead`, `sale.order`
5. **Service** — maintaining product value after sale
   - Data: `project.task` (support)

## Support Activities

6. **Firm Infrastructure** — general management, finance, legal
7. **Human Resource Management** — recruiting, training, compensation
8. **Technology Development** — R&D, process automation
9. **Procurement** — purchasing inputs

## Process
1. Map each Odoo module to value chain activities
2. Analyze cost and time per activity from Odoo data
3. Identify bottlenecks (longest lead times, highest costs)
4. Recommend optimization (automation, outsourcing, integration)
