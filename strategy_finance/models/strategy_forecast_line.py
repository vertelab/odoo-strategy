# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StrategyForecastLine(models.Model):
    _name = 'strategy.forecast.line'
    _description = 'Strategy Forecast Line (Monthly/Quarterly)'
    _order = 'date'

    forecast_id = fields.Many2one('strategy.forecast', 'Forecast',
        required=True, ondelete='cascade')
    date = fields.Date('Date', required=True, index=True)
    revenue = fields.Monetary('Revenue', currency_field='currency_id')
    cost = fields.Monetary('Cost', currency_field='currency_id')
    profit = fields.Monetary('Profit', currency_field='currency_id',
        compute='_compute_profit', store=True)
    cumulative_profit = fields.Monetary('Cumulative Profit',
        currency_field='currency_id', compute='_compute_cumulative', store=True)
    note = fields.Char('Note',
        help="e.g. 'Q4 seasonality', 'New hire starts', 'Product launch'")

    currency_id = fields.Many2one(related='forecast_id.currency_id')
    company_id = fields.Many2one(related='forecast_id.company_id')

    @api.depends('revenue', 'cost')
    def _compute_profit(self):
        for line in self:
            line.profit = line.revenue - line.cost

    @api.depends('date', 'profit', 'forecast_id.line_ids.profit')
    def _compute_cumulative(self):
        for forecast in self.mapped('forecast_id'):
            cumulative = 0.0
            for line in forecast.line_ids.sorted('date'):
                cumulative += line.profit
                line.cumulative_profit = cumulative
