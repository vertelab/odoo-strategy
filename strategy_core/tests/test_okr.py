# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestOKR(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.OKR = cls.env['okr.objective']
        cls.KR = cls.env['okr.key.result']

    def test_create_okr(self):
        objective = self.OKR.create({
            'name': 'Increase market share',
            'description': '<p>Grow from 10% to 15% in Sweden</p>',
        })
        self.assertEqual(objective.progress, 0.0)

    def test_key_result_progress(self):
        objective = self.OKR.create({'name': 'Revenue growth'})
        kr = self.KR.create({
            'objective_id': objective.id,
            'name': 'Reach 1M SEK MRR',
            'target_value': 1000000.0,
            'current_value': 650000.0,
        })
        self.assertEqual(kr.progress, 65.0)

    def test_objective_progress_average(self):
        objective = self.OKR.create({'name': 'Customer growth'})
        self.KR.create({
            'objective_id': objective.id,
            'name': '100 new customers',
            'target_value': 100.0,
            'current_value': 50.0,
        })
        self.KR.create({
            'objective_id': objective.id,
            'name': '50 enterprise customers',
            'target_value': 50.0,
            'current_value': 25.0,
        })
        # Both KRs at 50% → objective at 50%
        self.assertEqual(objective.progress, 50.0)

    def test_zero_target(self):
        kr = self.KR.create({
            'objective_id': self.OKR.create({'name': 'Test'}).id,
            'name': 'No target set',
            'target_value': 0.0,
            'current_value': 100.0,
        })
        self.assertEqual(kr.progress, 0.0)
