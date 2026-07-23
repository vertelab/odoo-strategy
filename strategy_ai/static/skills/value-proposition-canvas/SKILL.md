---
name: value-proposition-canvas
description: Create a Value Proposition Canvas mapping customer jobs, pains, gains to products.
  Triggers: "VPC", "value proposition canvas", "customer profile", "value map",
  "jobs to be done", "pains and gains".
metadata:
  version: 1.0.0
---

# Value Proposition Canvas

Map customer needs to your value proposition using Odoo data.

## Data Sources

- `crm.lead`: customer needs, pain points from sales conversations
- `sale.order`: what customers actually buy
- `product.template`: products and services offered
- `res.partner`: customer segments and feedback

## Customer Profile (right side)

1. **Customer Jobs** — what are customers trying to get done?
   - Functional jobs, social jobs, emotional jobs
2. **Pains** — what annoys or frustrates customers?
   - Obstacles, risks, negative outcomes
3. **Gains** — what outcomes do customers want?
   - Required, expected, desired, unexpected gains

## Value Map (left side)

4. **Products & Services** — what you offer
5. **Pain Relievers** — how you address pains
6. **Gain Creators** — how you create gains

## Process
1. Extract customer jobs/pains/gains from CRM lead descriptions
2. Map products to pain relievers and gain creators
3. Identify fit: do pain relievers address real pains? Do gain creators create real gains?
4. Flag gaps where customer needs are unmet by current products
5. Store as `value.proposition.canvas` record linked to BMC
