# Odoo Strategy — Business Modeling & Strategy Tools

**`odoo-strategy`** provides AI-powered business strategy tools integrated with Odoo.
It answers the question *WHAT* should the business do. The companion repo
[`odoo-marketing`](https://github.com/vertelab/odoo-marketing) answers *HOW* to execute.

## Modules

| Module | Description |
|--------|-------------|
| `strategy_core` | Business Model Canvas, SWOT, VPC, OKR, Porter, Blue Ocean, Ansoff, BCG, Risk Matrix, RACI |
| `strategy_finance` | Financial forecasts, TAM/SAM/SOM, unit economics, scenario modeling, pricing |
| `strategy_dashboard_vrtl` | Dashboard sources for strategy KPIs |

## Skills

All strategy skills are stored as `SKILL.md` files in `skills/` and imported
into Odoo as `marketing.skill` records at module install. Pi agents read them
via XML-RPC.

## Architecture

```
odoo-strategy (WHAT)              →  odoo-marketing (HOW)
──────────────────────                ──────────────────────
business.model.canvas                 marketing.plan
  • customer_segments        ──→        • target_audience
  • value_propositions       ──→        • key_message
  • channels                 ──→        • channel_mix
  • revenue_streams          ──→        • revenue_model

strategy.forecast + scenarios  ──→     marketing.plan (financial)
```

## Quick Start

```bash
# Clone and install
git clone git@github.com:vertelab/odoo-strategy.git /usr/share/odoo-strategy
cd /usr/share/odoo-strategy
python3 scripts/build_skill_xml.py
sudo checkmodule -d <db> -m strategy_core
```

## License

AGPL-3 — see [LICENSE](LICENSE)

## AI-integration (bridges)

**Princip: AI-förmågor (coworkers, skills, sessions) läggs ENBART i `_ai`-moduler — aldrig i domän-core.**

| Modul | Roll |
|-------|------|
| `strategy_core` | Ren domänlogik (BMC, SWOT, OKR, risk, möten) — **ingen AI-kod** |
| `strategy_ai` | **AI-brygga**: OKR Coach + Risk Analyst (ai.coworker-data), 2 ai.skill-poster; OKR→ai.org.goal-bridge (idempotent, external_ref-nyckel); Strategy Composer/Advisor/Review skapas av `ai_agent_core_strategy` (post_init_hook, ai.coworker) |
| `strategy_finance` | Finansiella strategi-tillägg (forecasts) |

### OKR-bridge
`strategy_ai/models/okr_bridge.py` speglar `okr.objective` → `ai.org.goal` och
`okr.key.result` → `ai.org.key.result` idempotent (söknyckel `external_ref =
'okr.objective,<id>'`). Triggas automatiskt vid create/write; knapp
`action_sync_ai_goal` finns på OKR-formuläret.
