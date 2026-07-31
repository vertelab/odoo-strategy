# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    """Extend hr.employee with board and management team fields."""

    _inherit = 'hr.employee'

    # -- Board of Directors -----------------------------------------------
    is_board_member = fields.Boolean(
        'Board Member', default=False,
        help="Is this employee a member of the Board of Directors?")
    board_role = fields.Selection([
        ('chairman', 'Chairman'),
        ('vice_chairman', 'Vice Chairman'),
        ('member', 'Member'),
        ('deputy', 'Deputy Member'),
        ('none', 'None'),
    ], string='Board Role', default='none')
    board_appointed_date = fields.Date('Appointed Date')
    board_term_end = fields.Date('Term End')

    # -- Management Team --------------------------------------------------
    is_management_team = fields.Boolean(
        'Management Team', default=False,
        help="Is this employee part of the management team?")
    management_role = fields.Selection([
        ('ceo', 'CEO'),
        ('cfo', 'CFO'),
        ('coo', 'COO'),
        ('cto', 'CTO'),
        ('cmo', 'CMO'),
        ('chro', 'CHRO'),
        ('cio', 'CIO'),
        ('other', 'Other'),
    ], string='Management Role')
    management_role_other = fields.Char(
        'Other Role',
        help="Specify role when Management Role is 'Other'")

    # -- Computed helpers -------------------------------------------------
    board_member_count = fields.Integer(
        'Board Members', compute='_compute_board_stats')
    management_team_count = fields.Integer(
        'Management Team', compute='_compute_board_stats')

    @api.depends()
    def _compute_board_stats(self):
        for rec in self:
            rec.board_member_count = self.search_count(
                [('is_board_member', '=', True)])
            rec.management_team_count = self.search_count(
                [('is_management_team', '=', True)])
