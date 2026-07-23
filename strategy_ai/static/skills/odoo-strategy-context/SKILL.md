---
name: odoo-strategy-context
description: Connect Pi agent to Odoo strategy tools via XML-RPC.
  Use when any strategy skill needs Odoo context — BMC data, CRM pipeline,
  sale orders, or customer profiles. Automatically activated when Pi loads
  a strategy skill from Odoo.
metadata:
  version: 1.0.0
---

# Odoo Strategy Context

You are connected to an Odoo instance via XML-RPC. All strategy data lives in
Odoo models. You read and write exclusively through XML-RPC — never filesystem.

## Connection

```python
import xmlrpc.client

# Credentials from Salt pillar (odoo_pi_agent user)
url = "https://{customer}.vertel.se"
db = "{customer}_db"
username = "pi_agent"
password = os.environ.get("ODOO_PI_PASSWORD")

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
```

## Core Strategy Models

### `business.model.canvas` — Read & Write

```python
# List all BMCs
bmcs = models.execute_kw(db, uid, pwd,
    'business.model.canvas', 'search_read',
    [[['state', '!=', 'archived']]],
    {'fields': ['name', 'customer_id', 'state', 'customer_segments',
                'value_propositions', 'revenue_streams', 'cost_structure']})

# Get live context for a BMC
ctx = models.execute_kw(db, uid, pwd,
    'business.model.canvas', 'get_live_context',
    [[bmc_id]])

# Create/Update BMC
models.execute_kw(db, uid, pwd,
    'business.model.canvas', 'write',
    [[bmc_id], {'value_propositions': '...'}])
```

### `swot.analysis` — Read & Write

```python
models.execute_kw(db, uid, pwd,
    'swot.analysis', 'create',
    [{'name': 'SWOT for ACME', 'bmc_id': bmc_id,
      'strengths': '...', 'weaknesses': '...'}])
```

### `strategy.risk` — Read & Write

```python
models.execute_kw(db, uid, pwd,
    'strategy.risk', 'create',
    [{'name': 'Market contraction risk', 'category': 'market',
      'probability': 'medium', 'impact_amount': 500000}])
```

## Base Data (read-only)

```python
# CRM pipeline
leads = models.execute_kw(db, uid, pwd,
    'crm.lead', 'search_read',
    [[['type', '=', 'opportunity']]],
    {'fields': ['name', 'stage_id', 'expected_revenue', 'probability']})

# Sales history
sales = models.execute_kw(db, uid, pwd,
    'sale.order', 'search_read',
    [[['state', 'in', ['sale', 'done']]]],
    {'fields': ['amount_total', 'date_order', 'partner_id']})

# Products
products = models.execute_kw(db, uid, pwd,
    'product.template', 'search_read',
    [[]],
    {'fields': ['name', 'list_price', 'standard_price', 'categ_id']})
```

## Security Constraints

- **Read-only** on: `res.partner`, `crm.lead`, `sale.order`, `account.move`
- **Read & Write** on: all `strategy_core` models (`business.model.canvas`,
  `swot.analysis`, `value.proposition.canvas`, `okr.objective`,
  `okr.key.result`, `strategy.risk`, `strategy.action`)
- **Never** modify user passwords, company settings, or accounting data
