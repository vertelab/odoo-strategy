# -*- coding: utf-8 -*-
{
    'name': 'Strategy AI Bridge',
    'version': '18.0.1.0.0',
    'summary': 'AI-powered strategy tools — bridge between strategy models and AI agents.',
    'description': '''
Strategy AI Bridge
==================

    AI-powered strategy tools — bridge between strategy models and AI agents.

    Features:

        - UI Integration: Extends 2 view(s) in the Odoo interface.
        - Extends Odoo: Builds on ai.org.goal, business.model.canvas, okr.key.result, okr.objective.
    ''',
    'category': 'Strategy',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-strategy/strategy_ai',
    'license': 'AGPL-3',
    'depends': ['strategy_core', 'ai_agent_core'],
    'data': [
        'security/ir.model.access.csv',
        'data/graph_definitions.xml',
        'data/strategy_skills.xml',
        'data/strategy_coworkers.xml',
        'views/strategy_plan_buttons.xml',
        'views/bmc_buttons.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
