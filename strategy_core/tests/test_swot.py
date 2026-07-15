# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSWOTAnalysis(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SWOT = cls.env['swot.analysis']
        cls.BMC = cls.env['business.model.canvas']
        cls.bmc = cls.BMC.create({'name': 'Test BMC'})

    def test_create_swot(self):
        swot = self.SWOT.create({
            'name': 'Test SWOT',
            'bmc_id': self.bmc.id,
            'strengths': '<p>Strong brand</p>',
            'weaknesses': '<p>Limited distribution</p>',
            'opportunities': '<p>New market segment</p>',
            'threats': '<p>New competitor</p>',
        })
        self.assertEqual(swot.state, 'draft')
        self.assertEqual(swot.bmc_id, self.bmc)
        self.assertIn('Strong', swot.strengths)

    def test_swot_linked_to_bmc(self):
        swot = self.SWOT.create({
            'name': 'Linked SWOT',
            'bmc_id': self.bmc.id,
        })
        self.assertIn(swot, self.bmc.swot_ids)
