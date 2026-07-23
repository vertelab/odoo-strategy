# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StrategyRisk(models.Model):
    _name = 'strategy.risk'
    _description = 'Strategic Risk'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'abs_impact_amount desc'

    name = fields.Char('Risk', required=True)
    plan_id = fields.Many2one('strategy.plan', 'Strategic Plan', ondelete='set null')
    bmc_id = fields.Many2one('business.model.canvas', 'Business Model Canvas', ondelete='cascade')
    forecast_id = fields.Many2one('strategy.forecast', 'Forecast', ondelete='set null')
    initiative_id = fields.Many2one('strategy.initiative', 'Initiative', ondelete='set null')
    category = fields.Selection([
        ('market', 'Market Risk'), ('competitive', 'Competitive Risk'),
        ('financial', 'Financial Risk'), ('operational', 'Operational Risk'),
        ('regulatory', 'Regulatory Risk'), ('technology', 'Technology Risk'),
        ('other', 'Other'),
    ], string='Category', required=True)
    probability = fields.Selection([
        ('low', 'Low (0-25%)'), ('medium', 'Medium (25-50%)'),
        ('high', 'High (50-75%)'), ('critical', 'Critical (75-100%)'),
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
