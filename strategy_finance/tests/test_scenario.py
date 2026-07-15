# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestStrategyScenario(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.BMC = cls.env['business.model.canvas']
        cls.Forecast = cls.env['strategy.forecast']
        cls.Scenario = cls.env['strategy.scenario']
        cls.ScenarioLine = cls.env['strategy.scenario.line']

        cls.bmc = cls.BMC.create({'name': 'Scenario Test BMC'})
        cls.forecast = cls.Forecast.create({
            'name': 'Scenario Forecast',
            'bmc_id': cls.bmc.id,
            'date_from': '2026-01-01',
            'date_to': '2026-01-31',
            'period': 'monthly',
        })
        cls.forecast.action_compute()

    def test_create_scenario(self):
        scenario = self.Scenario.create({
            'name': 'Optimistic',
            'forecast_id': self.forecast.id,
        })
        self.assertEqual(scenario.state, 'computed')

    def test_percentage_adjustment(self):
        scenario = self.Scenario.create({
            'name': 'Price +20%',
            'forecast_id': self.forecast.id,
        })
        line_date = self.forecast.line_ids[0].date
        self.ScenarioLine.create({
            'scenario_id': scenario.id,
            'category': 'price',
            'date': line_date,
            'percentage': 20.0,
            'label': '20% price increase',
        })
        self.assertEqual(scenario.state, 'computed')

    def test_absolute_adjustment(self):
        scenario = self.Scenario.create({
            'name': 'Cost cut',
            'forecast_id': self.forecast.id,
        })
        line_date = self.forecast.line_ids[0].date
        self.ScenarioLine.create({
            'scenario_id': scenario.id,
            'category': 'cost',
            'date': line_date,
            'amount': -5000.0,
            'label': 'Reduce office costs',
        })
        self.assertTrue(scenario.profit_impact)

    def test_scenario_linked_to_forecast(self):
        scenario = self.Scenario.create({
            'name': 'Linked Test',
            'forecast_id': self.forecast.id,
        })
        self.assertIn(scenario, self.forecast.scenario_ids)
