# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OkrObjective(models.Model):
    _name = 'okr.objective'
    _description = 'OKR Objective'
    _order = 'sequence, id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(default=10)
    name = fields.Char('Objective', required=True, tracking=True)
    description = fields.Html('Description')
    plan_id = fields.Many2one('strategy.plan', 'Strategic Plan', ondelete='set null', tracking=True)
    bmc_id = fields.Many2one('business.model.canvas', 'Business Model Canvas', ondelete='set null')
    customer_id = fields.Many2one('res.partner', 'Customer', ondelete='set null')
    department_id = fields.Many2one('hr.department', 'Department',
        tracking=True,
        help='Department that owns this OKR. Leave empty for strategic/company-level OKRs.')
    parent_id = fields.Many2one('okr.objective', 'Parent OKR',
        tracking=True,
        help='The strategic OKR this department OKR supports. Only relevant when '
             'department_id is set — creates a cascade: strategic → department → individual.')
    child_ids = fields.One2many('okr.objective', 'parent_id', 'Department OKRs')
    key_result_ids = fields.One2many('okr.key.result', 'objective_id', 'Key Results')
    progress = fields.Float('Progress', compute='_compute_progress', store=True, aggregator='avg')
    state = fields.Selection([
        ('draft', 'Draft'), ('active', 'Active'),
        ('achieved', 'Achieved'), ('cancelled', 'Cancelled'),
    ], string='State', default='draft', tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('key_result_ids.progress', 'child_ids.progress')
    def _compute_progress(self):
        for obj in self:
            # If this OKR has child department OKRs, aggregate from them
            if obj.child_ids:
                child_progresses = obj.child_ids.mapped('progress')
                obj.progress = sum(child_progresses) / len(child_progresses)
            # Otherwise use direct key results
            else:
                krs = obj.key_result_ids
                obj.progress = sum(krs.mapped('progress')) / len(krs) if krs else 0.0

    def action_activate(self): self.write({'state': 'active'})
    def action_achieve(self): self.write({'state': 'achieved'})
    def action_cancel(self): self.write({'state': 'cancelled'})

    def _get_salience_level(self):
        """Return salience level for nudge color coding.
        🔴 critical (<60%), ⚠️ warning (60-80%), ✅ ok (>80%)."""
        self.ensure_one()
        if self.progress < 60:
            return 'critical'
        elif self.progress < 80:
            return 'warning'
        return 'ok'

    def open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'okr.objective',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }


class OkrKeyResult(models.Model):
    _name = 'okr.key.result'
    _description = 'OKR Key Result'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    name = fields.Char('Key Result', required=True)
    objective_id = fields.Many2one('okr.objective', 'Objective', required=True, ondelete='cascade')
    target_value = fields.Float('Target Value', required=True, default=100.0)
    current_value = fields.Float('Current Value', default=0.0)
    unit = fields.Char('Unit', default='%')
    progress = fields.Float('Progress %', compute='_compute_progress', store=True)
    description = fields.Html('Description')

    @api.depends('current_value', 'target_value')
    def _compute_progress(self):
        for kr in self:
            kr.progress = (kr.current_value / kr.target_value) * 100.0 if kr.target_value else 0.0
