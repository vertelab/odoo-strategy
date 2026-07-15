# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, fields, models


class StrategyScenario(models.Model):
    """What-if scenario analysis for strategy forecasts.
    Inspired by liquidity.scenario: baseline + adjustments → recomputed outcomes."""

    _name = 'strategy.scenario'
    _description = 'Strategy What-If Scenario'
    _order = 'name'

    name = fields.Char('Scenario Name', required=True)
    forecast_id = fields.Many2one('strategy.forecast', 'Baseline Forecast',
        required=True, ondelete='cascade')
    line_ids = fields.One2many('strategy.scenario.line', 'scenario_id',
        string='Adjustments')

    # Computed outcomes (vs baseline)
    new_total_revenue = fields.Monetary('Scenario Revenue',
        currency_field='currency_id', compute='_compute_scenario', store=True)
    new_total_cost = fields.Monetary('Scenario Cost',
        currency_field='currency_id', compute='_compute_scenario', store=True)
    new_total_profit = fields.Monetary('Scenario Profit',
        currency_field='currency_id', compute='_compute_scenario', store=True)
    new_break_even_date = fields.Date('Scenario Break-Even',
        compute='_compute_scenario', store=True)
    new_profit_margin = fields.Float('Scenario Margin %',
        compute='_compute_scenario', store=True)
    revenue_impact = fields.Monetary('Revenue Impact (Δ)',
        currency_field='currency_id', compute='_compute_scenario', store=True)
    profit_impact = fields.Monetary('Profit Impact (Δ)',
        currency_field='currency_id', compute='_compute_scenario', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
    ], string='State', default='computed')

    company_id = fields.Many2one(related='forecast_id.company_id')
    currency_id = fields.Many2one(related='forecast_id.currency_id')

    @api.depends('line_ids.amount', 'line_ids.percentage', 'line_ids.date',
                 'forecast_id.line_ids.revenue', 'forecast_id.line_ids.cost')
    def _compute_scenario(self):
        for scenario in self:
            forecast = scenario.forecast_id
            if not forecast or forecast.state != 'computed':
                scenario._set_zeros()
                continue

            lines = forecast.line_ids.sorted('date')
            if not lines:
                scenario._set_zeros()
                continue

            # Sum adjustments
            adj_map = {}
            for adj in scenario.line_ids:
                d = str(adj.date)
                adj_map.setdefault(d, {'revenue': 0.0, 'cost': 0.0})

                if adj.percentage and not adj.amount:
                    # Percentage-based adjustment: apply to baseline
                    bl = next((l for l in lines if str(l.date) == d), None)
                    if bl:
                        if adj.category in ('revenue', 'price', 'volume'):
                            adj_map[d]['revenue'] += bl.revenue * (adj.percentage / 100.0)
                        elif adj.category in ('cost', 'cac'):
                            adj_map[d]['cost'] += bl.cost * (adj.percentage / 100.0)
                elif adj.amount:
                    if adj.category in ('revenue', 'price', 'volume'):
                        adj_map[d]['revenue'] += adj.amount
                    elif adj.category in ('cost', 'cac'):
                        adj_map[d]['cost'] += adj.amount

            # Recompute totals with adjustments
            total_rev = total_cost = 0.0
            cumulative = 0.0
            be_date = False
            today = date.today()

            for line in lines:
                d = str(line.date)
                adj = adj_map.get(d, {'revenue': 0.0, 'cost': 0.0})
                rev = line.revenue + adj['revenue']
                cost = line.cost + adj['cost']
                profit = rev - cost
                total_rev += rev
                total_cost += cost
                cumulative += profit
                if not be_date and cumulative > 0:
                    be_date = line.date

            scenario.new_total_revenue = total_rev
            scenario.new_total_cost = total_cost
            scenario.new_total_profit = total_rev - total_cost
            scenario.new_profit_margin = (
                ((total_rev - total_cost) / total_rev * 100) if total_rev else 0.0
            )
            scenario.new_break_even_date = be_date
            scenario.revenue_impact = total_rev - forecast.total_revenue
            scenario.profit_impact = (total_rev - total_cost) - forecast.total_profit

    def _set_zeros(self):
        self.new_total_revenue = 0.0
        self.new_total_cost = 0.0
        self.new_total_profit = 0.0
        self.new_profit_margin = 0.0
        self.new_break_even_date = False
        self.revenue_impact = 0.0
        self.profit_impact = 0.0


class StrategyScenarioLine(models.Model):
    _name = 'strategy.scenario.line'
    _description = 'Scenario Adjustment Line'

    scenario_id = fields.Many2one('strategy.scenario', 'Scenario',
        required=True, ondelete='cascade')
    category = fields.Selection([
        ('revenue', 'Revenue Change'),
        ('cost', 'Cost Change'),
        ('price', 'Price Change'),
        ('volume', 'Volume Change'),
        ('cac', 'CAC Change'),
        ('timing', 'Timing Shift'),
        ('other', 'Other'),
    ], string='Category', required=True)
    date = fields.Date('Date', required=True)
    amount = fields.Monetary('Amount (absolute)', currency_field='currency_id')
    percentage = fields.Float('Percentage Change',
        help="e.g. 20.0 = +20% adjustment")
    label = fields.Char('Description')

    currency_id = fields.Many2one(related='scenario_id.currency_id')
    company_id = fields.Many2one(related='scenario_id.company_id')
