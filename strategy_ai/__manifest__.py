# -*- coding: utf-8 -*-
{
    'name': 'Strategy AI Bridge',
    'version': '18.0.1.0.0',
    'summary': 'AI-powered strategy tools — bridge between strategy models and AI agents',
    'category': 'Strategy',
    'author': 'Vertel AB',
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
