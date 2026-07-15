# Odoo Strategy — Developer Guide

## Project Overview

This repo is part of Vertel's Odoo ecosystem. It provides business strategy tools
that feed into `odoo-marketing` for execution.

See [README.md](README.md) for user-facing documentation.

## Development

```bash
# Install modules
sudo checkmodule -d <db> -m strategy_core

# With tests
sudo checkmodule -d <db> -m strategy_core -t

# Build skill XML from SKILL.md files
python3 scripts/build_skill_xml.py

# Run tests
sudo -u odoo odoo shell -d <db> --no-http -c "env['ir.module.module'].search([('name','=','strategy_core')]).tests_ids"
```

## Conventions

- All secrets in Salt pillar, never in files
- Skills stored as SKILL.md in `skills/`, imported via data XML
- Module author: Vertel Sverige AB
- License: AGPL-3
- English-only code, sv.po for user-facing strings

## Skill Development

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter
2. Run `python3 scripts/build_skill_xml.py` to regenerate `data/strategy_skill.xml`
3. Install/upgrade module: `sudo checkmodule -d <db> -m strategy_core`
4. Skills are now available via `marketing.skill` in Odoo and XML-RPC

## Dependencies

- `strategy_core`: `base`, `mail`, `crm`, `sale_management`, `account`
- `strategy_finance`: `strategy_core`, `account`
- `strategy_dashboard_vrtl`: `strategy_finance`, `dashboard_vrtl`
