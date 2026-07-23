---
name: tam-sam-som
description: Calculate TAM, SAM, SOM from Odoo CRM and sales data.
  Triggers: "TAM SAM SOM", "market sizing", "total addressable market",
  "serviceable market", "obtainable market", "market size".
metadata:
  version: 1.0.0
---

# TAM / SAM / SOM Market Sizing

Calculate market size tiers from Odoo data.

## Data Sources

- `res.partner`: total addressable entities (TAM basis)
- `crm.lead`: qualified pipeline (SAM basis)
- `sale.order`: actual won revenue (SOM basis)
- Industry and geography filters from partner data

## Three Tiers

1. **TAM (Total Addressable Market)** — everyone who could use your product
   - Count: all partners matching ICP criteria
   - Value: estimated total market spend

2. **SAM (Serviceable Addressable Market)** — those you can realistically reach
   - Count: qualified leads + existing customers
   - Value: pipeline expected value

3. **SOM (Serviceable Obtainable Market)** — what you can realistically capture
   - Count: won deals in last 12 months
   - Value: actual revenue

## Process
1. Define ICP criteria (industry, size, geography)
2. Count TAM from partner database
3. Measure SAM from CRM pipeline
4. Calculate SOM from actual sales
5. Compute SAM/TAM ratio (market penetration)
6. Compute SOM/SAM ratio (win rate)
