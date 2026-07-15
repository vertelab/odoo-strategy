# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Vertel Dashboard — Strategy Sources',
    'version': '18.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Dashboard adapters for odoo-strategy data',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'depends': ['dashboard_vrtl', 'strategy_finance'],
    'data': [
        'data/dashboards/strategy_overview.yaml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
