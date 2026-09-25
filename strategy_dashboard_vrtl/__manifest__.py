# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Vertel Dashboard — Strategy Sources',
    'version': '18.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Dashboard adapters for odoo-strategy data.',
    'description': '''
Vertel Dashboard — Strategy Sources
===================================

    Dashboard adapters for odoo-strategy data.

    Features:

        - Focused Fix: A small, targeted improvement to standard Odoo behaviour.
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-strategy/strategy_dashboard_vrtl',
    'license': 'AGPL-3',
    'depends': ['dashboard_vrtl', 'strategy_finance'],
    'data': [
        'data/dashboards/strategy_overview.yaml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
