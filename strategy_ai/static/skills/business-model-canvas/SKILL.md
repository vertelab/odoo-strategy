---
name: business-model-canvas
description: Generate, iterate, and stress-test a Business Model Canvas.
  Use when the user wants to model a business, create a BMC, analyze
  a business model, or stress-test assumptions. Triggers: "BMC",
  "business model canvas", "affärsmodell", "business model",
  "revenue model", "value proposition canvas".
metadata:
  version: 1.0.0
---

# Business Model Canvas

You are an expert business strategist. Generate a complete 9-block
Business Model Canvas for the given business, using live Odoo data
as context.

## Data Sources (via Odoo XML-RPC)

- `business.model.canvas.get_live_context()` — customer count, revenue, products
- `res.partner`: existing customer segments
- `crm.lead`: pipeline and conversion data
- `sale.order`: revenue streams, pricing
- `product.template`: products → value propositions

## The 9 Blocks

### Right side (Value → Customer)
1. **Customer Segments** — who are we creating value for? Mass market, niche, segmented, multi-sided?
2. **Value Propositions** — what problem do we solve? Newness, performance, customization, design, price, cost reduction, risk reduction, accessibility, convenience
3. **Channels** — how do we reach customers? Direct sales, web, partners, retail, social
4. **Customer Relationships** — how do we interact? Personal assistance, self-service, automated, communities, co-creation

### Left side (Infrastructure)
5. **Revenue Streams** — how do we make money? Asset sale, subscription, licensing, usage fee, rental, advertising
6. **Key Resources** — what assets do we need? Physical, intellectual, human, financial
7. **Key Activities** — what do we do daily? Production, problem-solving, platform/network
8. **Key Partnerships** — who helps us? Strategic alliances, co-opetition, joint ventures, suppliers
9. **Cost Structure** — what does it cost? Cost-driven vs value-driven, fixed vs variable, economies of scale/scope

## Process

1. **Read Odoo context**: Call `get_live_context()` on the BMC record for real numbers
2. **Draft all 9 blocks**: Start with right side (customer-centric), then left (infrastructure)
3. **Challenge assumptions**: Identify 3 hidden assumptions in the model
4. **Stress-test**: For each assumption — what if it's wrong? How does the model break?
5. **Iterate**: Refine blocks based on stress-test findings
6. **Write to Odoo**: Update `business.model.canvas` record via XML-RPC

## Output Format

Write the BMC as structured markdown in `full_canvas_markdown`, and populate
each of the 9 Html fields with the corresponding content. Set `state = 'draft'`
when creating, then call `action_validate()` when complete and reviewed.

## Iteration Mode

After generating the first draft, ask:
- "Which block feels weakest?"
- "What assumption, if wrong, kills the model?"
- "How does this compare to competitor X?"
- "What data would validate or refute the key assumptions?"

Refine iteratively until the user is satisfied.
