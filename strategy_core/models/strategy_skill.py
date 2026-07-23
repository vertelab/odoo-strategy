# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StrategySkill(models.Model):
    _name = 'strategy.skill'
    _description = 'Strategy Skill'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, tracking=True)
    description = fields.Text('Description')
    category = fields.Selection([
        ('analysis', 'Analysis'),
        ('planning', 'Planning'),
        ('pricing', 'Pricing'),
        ('strategy', 'Strategy & Planning'),
    ], string='Category', default='strategy', required=True)
    version = fields.Char('Version', default='1.0.0')
    skill_content = fields.Text('Skill Content (Markdown)')
    is_base = fields.Boolean('Base Skill', default=True)
    is_active = fields.Boolean('Active', default=True)
    bmc_ids = fields.One2many('business.model.canvas', 'skill_id', string='Generated BMCs')

    def action_mark_base(self): self.write({'is_base': True})
    def action_unmark_base(self): self.write({'is_base': False})
    def action_toggle_active(self): self.write({'is_active': not self.is_active})
