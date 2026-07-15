# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Strategy Core',
    'version': '18.0.1.0.0',
    'category': 'Strategy',
    'summary': 'Business strategy tools — BMC, SWOT, VPC, OKR, Porter, Ansoff, BCG, Risk Matrix',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-strategy',
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'crm', 'sale_management', 'account', 'marketing_core'],
    'data': [
        'security/strategy_security.xml',
        'security/ir.model.access.csv',
        'data/strategy_skill.xml',
        'views/strategy_menu_views.xml',
        'views/bmc_views.xml',
        'views/swot_views.xml',
        'views/vpc_views.xml',
        'views/okr_views.xml',
        'views/strategy_risk_views.xml',
        'views/strategy_action_views.xml',
        'wizards/skill_import_wizard_views.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'strategy_core/static/src/js/bmc_canvas.js',
            'strategy_core/static/src/scss/strategy.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
