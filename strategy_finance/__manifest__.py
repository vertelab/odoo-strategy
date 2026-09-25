# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Strategy Finance',
    'version': '18.0.1.0.0',
    'category': 'Strategy',
    'summary': 'Financial forecasts and scenario modeling for business strategy.',
    'description': '''
Strategy Finance
================

    Financial forecasts and scenario modeling for business strategy.

    Features:

        - UI Integration: Extends 2 view(s) in the Odoo interface.
        - Extends Odoo: Builds on strategy.forecast, strategy.forecast.line, strategy.scenario, strategy.scenario.line.
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-strategy/strategy_finance',
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
