---
name: swot-analysis
description: Generate a SWOT analysis from Odoo business data.
  Use when the user wants to analyze strengths, weaknesses, opportunities,
  and threats. Triggers: "SWOT", "strengths weaknesses", "swot analysis".
metadata:
  version: 1.0.0
---

# SWOT Analysis

Generate a SWOT analysis based on live Odoo data.

## Data Sources

- `business.model.canvas`: existing BMC blocks
- `crm.lead`: pipeline strength (strengths) / gaps (weaknesses)
- `sale.order`: revenue trends (strengths) / declining products (weaknesses)
- `res.partner`: market reach (opportunities)
- `social_marketing.competitor`: competitive threats
- `strategy.risk`: existing identified risks

## The 4 Quadrants

### Strengths (internal, positive)
What does the business do well? Unique resources? Competitive advantages?

### Weaknesses (internal, negative)
What could be improved? Resource gaps? Where do competitors outperform?

### Opportunities (external, positive)
Market trends? Underserved segments? Technology shifts?

### Threats (external, negative)
Competitor moves? Regulatory changes? Market contraction?

## Process
1. Read BMC + Odoo data for context
2. Populate all 4 quadrants with specific, data-backed points
3. Cross-reference: strengths should address opportunities, mitigate threats
4. Output: `swot.analysis` record linked to BMC
