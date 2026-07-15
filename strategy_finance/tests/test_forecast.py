# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestStrategyForecast(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.BMC = cls.env['business.model.canvas']
        cls.Forecast = cls.env['strategy.forecast']
        cls.bmc = cls.BMC.create({'name': 'Forecast Test BMC'})

    def test_create_forecast(self):
        forecast = self.Forecast.create({
            'name': 'Q1 2026 Forecast',
            'bmc_id': self.bmc.id,
            'date_from': '2026-01-01',
            'date_to': '2026-03-31',
            'period': 'monthly',
        })
        self.assertEqual(forecast.state, 'draft')
        self.assertEqual(forecast.period, 'monthly')

    def test_compute_forecast(self):
        forecast = self.Forecast.create({
            'name': 'Test Compute',
            'bmc_id': self.bmc.id,
            'date_from': '2026-01-01',
            'date_to': '2026-01-31',
            'period': 'monthly',
        })
        forecast.action_compute()
        self.assertEqual(forecast.state, 'computed')
        self.assertTrue(forecast.line_ids)
        self.assertGreater(len(forecast.line_ids), 0)

    def test_totals_computed(self):
        forecast = self.Forecast.create({
            'name': 'Totals Test',
            'bmc_id': self.bmc.id,
            'date_from': '2026-01-01',
            'date_to': '2026-01-31',
            'period': 'monthly',
        })
        forecast.action_compute()

        self.assertGreaterEqual(forecast.total_revenue, 0.0)
        self.assertGreaterEqual(forecast.total_cost, 0.0)

    def test_line_profit(self):
        forecast = self.Forecast.create({
            'name': 'Line Test',
            'bmc_id': self.bmc.id,
            'date_from': '2026-01-01',
            'date_to': '2026-01-31',
            'period': 'monthly',
        })
        forecast.action_compute()
        line = forecast.line_ids[0]
        self.assertEqual(line.profit, line.revenue - line.cost)
