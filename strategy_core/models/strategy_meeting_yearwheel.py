# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""
Optional Year Wheel integration for recurring meeting scheduling.

This module provides predefined year.wheel records for board and management
meetings. The mgmtsystem_yearwheel module must be installed for this to work.
All imports are wrapped in try/except to make this dependency optional.
"""

import logging
from datetime import timedelta

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.mgmtsystem_yearwheel.models.year_wheel import YearWheel
    HAS_YEAR_WHEEL = True
except ImportError:
    HAS_YEAR_WHEEL = False
    _logger.info('mgmtsystem_yearwheel not installed — Year Wheel integration skipped')


class StrategyMeetingYearWheel(models.Model):
    """Extend strategy.meeting with year.wheel integration methods."""

    _inherit = 'strategy.meeting'

    def action_setup_recurring(self):
        """Create year.wheel records for recurring meetings if available."""
        self.ensure_one()
        if not HAS_YEAR_WHEEL:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Year Wheel Not Available'),
                    'message': _(
                        'Install mgmtsystem_yearwheel for recurring '
                        'meeting scheduling.'),
                    'type': 'warning',
                }
            }
        # Delegate to the predefined year wheel setup
        YearWheelSetup = self.env['strategy.meeting.yearwheel.setup']
        return YearWheelSetup.action_setup(self)


class YearWheelSetup(models.TransientModel):
    """Wizard/predefined setup for year wheel meeting scheduling."""

    _name = 'strategy.meeting.yearwheel.setup'
    _description = 'Year Wheel Meeting Setup'

    meeting_type = fields.Selection([
        ('board', 'Board of Directors'),
        ('management', 'Management Team'),
    ], string='Meeting Type', required=True)

    template_id = fields.Many2one(
        'strategy.meeting.template', 'Meeting Template')

    def action_setup(self, meeting=False):
        """Create or return predefined year.wheel records."""
        if not HAS_YEAR_WHEEL:
            return {'type': 'ir.actions.act_window_close'}

        ActivityType = self.env['mail.activity.type']
        YearWheel = self.env['year.wheel']

        # Ensure activity types exist
        board_activity = ActivityType.search([
            ('name', '=', 'Board Meeting'),
        ], limit=1)
        if not board_activity:
            board_activity = ActivityType.create({
                'name': 'Board Meeting',
                'category': 'meeting',
                'icon': 'fa-legal',
            })

        mgmt_activity = ActivityType.search([
            ('name', '=', 'Management Meeting'),
        ], limit=1)
        if not mgmt_activity:
            mgmt_activity = ActivityType.create({
                'name': 'Management Meeting',
                'category': 'meeting',
                'icon': 'fa-users',
            })

        template = self.template_id or meeting.template_id

        if not template:
            if self.meeting_type == 'board':
                template = self.env.ref(
                    'strategy_core.meeting_template_board', raise_if_not_found=False)
            else:
                template = self.env.ref(
                    'strategy_core.meeting_template_management', raise_if_not_found=False)

        res_model = 'strategy.meeting'
        res_id = meeting.id if meeting else False

        if self.meeting_type == 'board':
            existing = YearWheel.search([
                ('res_model', '=', res_model),
                ('res_id', '=', res_id or 0),
                ('summary', '=', 'Styrelsemöte'),
            ], limit=1)
            if not existing:
                YearWheel.create({
                    'res_model': res_model,
                    'res_id': res_id or 0,
                    'summary': 'Styrelsemöte',
                    'activity_wheel_type_id': board_activity.id,
                    'activity_due_in': 1,
                    'activity_due_interval': 'days',
                    'interval': 1,
                    'time_unit': 'months',
                    'start_date': fields.Date.today(),
                    'end_date': fields.Date.today() + timedelta(days=365),
                    'user_id': self.env.user.id,
                })

        if self.meeting_type == 'management':
            existing = YearWheel.search([
                ('res_model', '=', res_model),
                ('res_id', '=', res_id or 0),
                ('summary', '=', 'Ledningsgruppsmöte'),
            ], limit=1)
            if not existing:
                YearWheel.create({
                    'res_model': res_model,
                    'res_id': res_id or 0,
                    'summary': 'Ledningsgruppsmöte',
                    'activity_wheel_type_id': mgmt_activity.id,
                    'activity_due_in': 1,
                    'activity_due_interval': 'days',
                    'interval': 1,
                    'time_unit': 'weeks',
                    'start_date': fields.Date.today(),
                    'end_date': fields.Date.today() + timedelta(days=365),
                    'user_id': self.env.user.id,
                })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Year Wheel Created'),
                'message': _(
                    'Recurring %s meeting schedule has been set up.') % (
                    dict(self._fields['meeting_type'].selection).get(
                        self.meeting_type),
                ),
                'type': 'success',
            }
        }


class PredefinedYearWheelData(models.Model):
    """Predefined year.wheel records installed via data/xml."""

    _name = 'strategy.meeting.yearwheel.data'
    _description = 'Predefined Year Wheel Data (technical)'

    def _setup_predefined_wheels(self):
        """Create the predefined year wheel records if possible.
        Called from post_init_hook when strategy_core is installed/upgraded."""
        if not HAS_YEAR_WHEEL:
            _logger.info(
                'mgmtsystem_yearwheel not available — '
                'skipping predefined year wheel setup')
            return

        ActivityType = self.env['mail.activity.type']

        board_activity = ActivityType.search([
            ('name', '=', 'Board Meeting'),
        ], limit=1)
        if not board_activity:
            return  # Will be created when user first sets up

        # Create year.wheel records if they don't exist
        YearWheel = self.env['year.wheel']
        existing_board = YearWheel.search([
            ('res_model', '=', 'strategy.meeting'),
            ('summary', '=', 'Styrelsemöte'),
        ], limit=1)
        if not existing_board:
            YearWheel.create({
                'res_model': 'strategy.meeting',
                'res_id': 0,
                'summary': 'Styrelsemöte',
                'activity_wheel_type_id': board_activity.id,
                'activity_due_in': 1,
                'activity_due_interval': 'days',
                'interval': 1,
                'time_unit': 'months',
                'start_date': fields.Date.today(),
                'end_date': fields.Date.today() + timedelta(days=365),
                'user_id': self.env.user.id,
            })

        mgmt_activity = ActivityType.search([
            ('name', '=', 'Management Meeting'),
        ], limit=1)
        existing_mgmt = YearWheel.search([
            ('res_model', '=', 'strategy.meeting'),
            ('summary', '=', 'Ledningsgruppsmöte'),
        ], limit=1)
        if not existing_mgmt and mgmt_activity:
            YearWheel.create({
                'res_model': 'strategy.meeting',
                'res_id': 0,
                'summary': 'Ledningsgruppsmöte',
                'activity_wheel_type_id': mgmt_activity.id,
                'activity_due_in': 1,
                'activity_due_interval': 'days',
                'interval': 1,
                'time_unit': 'weeks',
                'start_date': fields.Date.today(),
                'end_date': fields.Date.today() + timedelta(days=365),
                'user_id': self.env.user.id,
            })

        _logger.info('Predefined year wheel records created')
