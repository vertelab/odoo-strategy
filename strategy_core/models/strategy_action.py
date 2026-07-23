# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StrategyAction(models.Model):
    _name = 'strategy.action'
    _description = 'Strategic Action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'effect_amount desc'

    name = fields.Char('Action', required=True)
    plan_id = fields.Many2one('strategy.plan', 'Strategic Plan', ondelete='set null')
    risk_id = fields.Many2one('strategy.risk', 'Risk', ondelete='cascade')
    forecast_id = fields.Many2one('strategy.forecast', 'Forecast', ondelete='set null')
    initiative_id = fields.Many2one('strategy.initiative', 'Initiative', ondelete='set null')
    action_type = fields.Selection([
        ('pivot_strategy', 'Pivot Strategy'), ('cut_costs', 'Cut Costs'),
        ('increase_prices', 'Increase Prices'), ('enter_market', 'Enter New Market'),
        ('exit_market', 'Exit Market'), ('acquire', 'Acquire Company/Asset'),
        ('divest', 'Divest'), ('raise_capital', 'Raise Capital'),
        ('hire_talent', 'Hire Key Talent'), ('invest_tech', 'Invest in Technology'),
        ('other', 'Other'),
    ], string='Action Type', required=True)
    description = fields.Html('Description')
    effect_amount = fields.Monetary('Estimated Effect', currency_field='currency_id')
    effect_description = fields.Char('Effect Description')
    state = fields.Selection([
        ('proposed', 'Proposed'), ('approved', 'Approved'),
        ('in_progress', 'In Progress'), ('completed', 'Completed'),
        ('dismissed', 'Dismissed'),
    ], string='State', default='proposed')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')

    def action_approve(self): self.write({'state': 'approved'})
    def action_start(self): self.write({'state': 'in_progress'})
    def action_complete(self): self.write({'state': 'completed'})
    def action_dismiss(self): self.write({'state': 'dismissed'})
