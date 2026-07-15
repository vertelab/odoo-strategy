# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StrategyRisk(models.Model):
    """Strategic risk factor — follows the liquidity.risk.driver pattern.
    Each forecast or BMC can have multiple identified risks."""

    _name = 'strategy.risk'
    _description = 'Strategic Risk'
    _order = 'abs_impact_amount desc'

    name = fields.Char('Risk', required=True)
    bmc_id = fields.Many2one('business.model.canvas', 'Business Model Canvas', ondelete='cascade')
    forecast_id = fields.Many2one('strategy.forecast', 'Financial Forecast', ondelete='cascade')

    category = fields.Selection([
        ('market', 'Market Risk'),
        ('competitive', 'Competitive Risk'),
        ('financial', 'Financial Risk'),
        ('operational', 'Operational Risk'),
        ('regulatory', 'Regulatory Risk'),
        ('technology', 'Technology Risk'),
        ('other', 'Other'),
    ], string='Category', required=True)

    probability = fields.Selection([
        ('low', 'Low (0-25%)'),
        ('medium', 'Medium (25-50%)'),
        ('high', 'High (50-75%)'),
        ('critical', 'Critical (75-100%)'),
    ], string='Probability', required=True)

    impact_amount = fields.Monetary('Impact Amount', currency_field='currency_id')
    abs_impact_amount = fields.Monetary('Absolute Impact', currency_field='currency_id',
        compute='_compute_abs', store=True)
    impact_description = fields.Html('Impact Description')

    mitigation = fields.Html('Mitigation Strategy')
    action_ids = fields.One2many('strategy.action', 'risk_id', 'Actions')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.depends('impact_amount')
    def _compute_abs(self):
        for r in self:
            r.abs_impact_amount = abs(r.impact_amount)


class StrategyAction(models.Model):
    """Strategic action — recommended response to a risk or opportunity.
    Follows the liquidity.action pattern (proposed → applied → dismissed)."""

    _name = 'strategy.action'
    _description = 'Strategic Action'
    _order = 'effect_amount desc'

    name = fields.Char('Action', required=True)
    risk_id = fields.Many2one('strategy.risk', 'Risk', ondelete='cascade')
    forecast_id = fields.Many2one('strategy.forecast', 'Forecast', ondelete='cascade')

    action_type = fields.Selection([
        ('pivot_strategy', 'Pivot Strategy'),
        ('cut_costs', 'Cut Costs'),
        ('increase_prices', 'Increase Prices'),
        ('enter_market', 'Enter New Market'),
        ('exit_market', 'Exit Market'),
        ('acquire', 'Acquire Company/Asset'),
        ('divest', 'Divest'),
        ('raise_capital', 'Raise Capital'),
        ('hire_talent', 'Hire Key Talent'),
        ('invest_tech', 'Invest in Technology'),
        ('other', 'Other'),
    ], string='Action Type', required=True)

    description = fields.Html('Description')
    effect_amount = fields.Monetary('Estimated Effect', currency_field='currency_id')
    effect_description = fields.Char('Effect Description')

    state = fields.Selection([
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('dismissed', 'Dismissed'),
    ], string='State', default='proposed', tracking=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_dismiss(self):
        self.write({'state': 'dismissed'})
