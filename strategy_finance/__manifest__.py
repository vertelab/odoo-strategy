# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Strategy Finance',
    'version': '18.0.1.0.0',
    'category': 'Strategy',
    'summary': 'Financial forecasts and scenario modeling for business strategy',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-strategy',
    'license': 'AGPL-3',
    'depends': ['strategy_core', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/strategy_forecast_views.xml',
        'views/strategy_scenario_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
