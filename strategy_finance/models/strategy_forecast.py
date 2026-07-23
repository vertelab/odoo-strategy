# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StrategyForecast(models.Model):
    """Financial forecast derived from Business Model Canvas.
    Follows the same pattern as liquidity.forecast:
    baseline → lines → risks → actions → scenarios."""

    _name = 'strategy.forecast'
    _description = 'Strategy Financial Forecast'
    _order = 'create_date desc, name'

    name = fields.Char('Name', required=True,
        default=lambda self: _('Forecast %s') % fields.Date.today())
    plan_id = fields.Many2one('strategy.plan', 'Strategic Plan', ondelete='set null')
    bmc_id = fields.Many2one('business.model.canvas', 'Business Model Canvas',
        required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')

    # Timeframe
    date_from = fields.Date('From', required=True, default=fields.Date.today)
    date_to = fields.Date('To', required=True)
    period = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Period', default='monthly', required=True)

    # Lines
    line_ids = fields.One2many('strategy.forecast.line', 'forecast_id',
        string='Forecast Lines')

    # Computed totals
    total_revenue = fields.Monetary('Total Revenue', currency_field='currency_id',
        compute='_compute_totals', store=True)
    total_cost = fields.Monetary('Total Cost', currency_field='currency_id',
        compute='_compute_totals', store=True)
    total_profit = fields.Monetary('Total Profit', currency_field='currency_id',
        compute='_compute_totals', store=True)
    break_even_date = fields.Date('Break-Even Date',
        compute='_compute_totals', store=True)
    profit_margin = fields.Float('Profit Margin %',
        compute='_compute_totals', store=True)

    # Risk & Actions (same pattern as liquidity)
    risk_ids = fields.One2many('strategy.risk', 'forecast_id',
        string='Strategic Risks')
    action_ids = fields.One2many('strategy.action', 'forecast_id',
        string='Strategic Actions')
    scenario_ids = fields.One2many('strategy.scenario', 'forecast_id',
        string='Scenarios')

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
        ('error', 'Error'),
    ], string='State', default='draft', required=True, tracking=True)
    computed_at = fields.Datetime('Computed At')

    @api.depends('line_ids.revenue', 'line_ids.cost', 'line_ids.profit')
    def _compute_totals(self):
        for forecast in self:
            lines = forecast.line_ids
            forecast.total_revenue = sum(lines.mapped('revenue'))
            forecast.total_cost = sum(lines.mapped('cost'))
            forecast.total_profit = forecast.total_revenue - forecast.total_cost
            forecast.profit_margin = (
                (forecast.total_profit / forecast.total_revenue * 100)
                if forecast.total_revenue else 0.0
            )

            # Break-even: first period where cumulative profit > 0
            cumulative = 0.0
            forecast.break_even_date = False
            for line in lines.sorted('date'):
                cumulative += line.profit
                if cumulative > 0 and not forecast.break_even_date:
                    forecast.break_even_date = line.date

    def action_compute(self):
        """Compute forecast from BMC data."""
        self.ensure_one()
        try:
            self.state = 'draft'
            self._generate_lines()
            self.state = 'computed'
            self.computed_at = fields.Datetime.now()
        except Exception as e:
            self.state = 'error'
            _logger.exception('Failed to compute forecast %s', self.id)
            raise UserError(_('Forecast computation failed: %s') % str(e))

    def _generate_lines(self):
        """Generate monthly forecast lines from BMC data.
        Override or extend for more sophisticated forecasting."""
        self.line_ids.unlink()

        bmc = self.bmc_id
        if not bmc:
            return

        # Parse revenue and cost from BMC blocks (simple heuristics)
        # In production, use AI or more sophisticated modeling
        monthly_revenue = self._estimate_monthly_revenue(bmc)
        monthly_cost = self._estimate_monthly_cost(bmc)

        current = self.date_from
        delta = {'monthly': timedelta(days=30),
                 'quarterly': timedelta(days=90),
                 'yearly': timedelta(days=365)}[self.period]

        while current <= self.date_to:
            self.env['strategy.forecast.line'].create({
                'forecast_id': self.id,
                'date': current,
                'revenue': monthly_revenue,
                'cost': monthly_cost,
            })
            current += delta

    def _estimate_monthly_revenue(self, bmc):
        """Estimate monthly revenue from BMC data or historical sales."""
        ctx = bmc.get_live_context()
        if ctx.get('revenue_12m'):
            return ctx['revenue_12m'] / 12.0
        return 0.0

    def _estimate_monthly_cost(self, bmc):
        """Estimate monthly cost from BMC data."""
        # Simple: assume 70% of revenue as cost if no better data
        revenue = self._estimate_monthly_revenue(bmc)
        return revenue * 0.7
