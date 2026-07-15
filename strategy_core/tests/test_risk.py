# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestStrategyRisk(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Risk = cls.env['strategy.risk']
        cls.Action = cls.env['strategy.action']
        cls.BMC = cls.env['business.model.canvas']
        cls.bmc = cls.BMC.create({'name': 'Risk Test BMC'})

    def test_create_risk(self):
        risk = self.Risk.create({
            'name': 'Market contraction',
            'bmc_id': self.bmc.id,
            'category': 'market',
            'probability': 'medium',
            'impact_amount': 500000.0,
        })
        self.assertEqual(risk.category, 'market')
        self.assertEqual(risk.probability, 'medium')
        self.assertEqual(risk.abs_impact_amount, 500000.0)

    def test_risk_abs_impact(self):
        risk = self.Risk.create({
            'name': 'Cost overrun',
            'bmc_id': self.bmc.id,
            'category': 'financial',
            'probability': 'high',
            'impact_amount': -250000.0,
        })
        self.assertEqual(risk.abs_impact_amount, 250000.0)

    def test_action_lifecycle(self):
        action = self.Action.create({
            'name': 'Enter German market',
            'action_type': 'enter_market',
            'description': '<p>Expand to DACH region</p>',
            'effect_amount': 1000000.0,
        })
        self.assertEqual(action.state, 'proposed')

        action.action_approve()
        self.assertEqual(action.state, 'approved')

        action.action_start()
        self.assertEqual(action.state, 'in_progress')

        action.action_complete()
        self.assertEqual(action.state, 'completed')

    def test_action_dismiss(self):
        action = self.Action.create({
            'name': 'Bad idea',
            'action_type': 'other',
        })
        action.action_dismiss()
        self.assertEqual(action.state, 'dismissed')

    def test_risk_linked_to_action(self):
        risk = self.Risk.create({
            'name': 'Supplier risk',
            'bmc_id': self.bmc.id,
            'category': 'operational',
            'probability': 'low',
        })
        action = self.Action.create({
            'name': 'Diversify suppliers',
            'action_type': 'other',
            'risk_id': risk.id,
        })
        self.assertIn(action, risk.action_ids)
