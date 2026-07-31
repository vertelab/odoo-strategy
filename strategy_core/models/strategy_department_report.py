# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Department Weekly Report — AI-generated brief with versioning,
review workflow, and nudge-metric logging."""

import logging
from datetime import date, timedelta, datetime

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class StrategyDepartmentReport(models.Model):
    _name = 'strategy.department.report'
    _description = 'Department Weekly Report'
    _order = 'week_start desc, department_id'
    _inherit = ['mail.thread']

    # -- Identity ----------------------------------------------------------
    department_id = fields.Many2one(
        'hr.department', 'Department', required=True,
        ondelete='cascade')
    manager_id = fields.Many2one(
        'hr.employee', 'Department Head',
        related='department_id.manager_id', store=True)
    week_start = fields.Date('Week Starting', required=True)
    week_end = fields.Date('Week Ending', compute='_compute_week_end', store=True)
    display_name = fields.Char(compute='_compute_display_name', store=True)

    # -- Content — versioned -------------------------------------------------
    content = fields.Html('AI Draft',
        help='Unmodified AI-generated content. Preserved for comparison.')
    edited_content = fields.Html('Reviewed Content',
        help='Department head\'s edited version of the report.')
    version = fields.Integer('Version', default=1)
    edit_distance = fields.Selection([
        ('none', 'Unchanged'),
        ('small', 'Minor Adjustments'),
        ('major', 'Major Changes'),
        ('regenerated', 'Regenerated'),
    ], string='Edit Distance')

    # -- Review workflow ---------------------------------------------------
    status = fields.Selection([
        ('draft', 'AI Draft'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
    ], string='Status', default='draft', tracking=True)
    reviewed_by = fields.Many2one('res.users', 'Reviewed By')
    reviewed_at = fields.Datetime('Reviewed At')

    # -- Connections -------------------------------------------------------
    agenda_item_id = fields.Many2one(
        'strategy.meeting.agenda.item', 'Agenda Item',
        help='Synced to this agenda item when approved.')
    discuss_channel_id = fields.Many2one(
        'discuss.channel', 'Discussion Channel')
    discuss_message_id = fields.Many2one(
        'mail.message', 'Channel Message')

    # -- Metrics -----------------------------------------------------------
    generated_at = fields.Datetime(
        'Generated At', default=lambda self: fields.Datetime.now())
    opened_at = fields.Datetime('First Opened')
    approved_at = fields.Datetime('Approved At')
    time_to_approve_hours = fields.Float(
        'Hours to Approve', compute='_compute_time_to_approve', store=True)

    # -- Kaizen ------------------------------------------------------------
    kaizen_report_id = fields.Many2one(
        'ai.kaizen.report', 'Kaizen Report')
    ai_generated = fields.Boolean('AI Generated', default=True)

    # -- Computed ----------------------------------------------------------
    @api.depends('week_start')
    def _compute_week_end(self):
        for r in self:
            if r.week_start:
                r.week_end = r.week_start + timedelta(days=6)

    @api.depends('department_id.name', 'week_start')
    def _compute_display_name(self):
        for r in self:
            dept = r.department_id.name if r.department_id else '?'
            week = r.week_start.isoformat() if r.week_start else '?'
            r.display_name = '%s — v%s' % (dept, week)

    @api.depends('generated_at', 'approved_at')
    def _compute_time_to_approve(self):
        for r in self:
            if r.generated_at and r.approved_at:
                delta = r.approved_at - r.generated_at
                r.time_to_approve_hours = delta.total_seconds() / 3600.0
            else:
                r.time_to_approve_hours = 0.0

    # -- Actions -----------------------------------------------------------
    def action_review(self):
        """Mark report as reviewed with current timestamp."""
        self.ensure_one()
        self.write({
            'status': 'reviewed',
            'reviewed_by': self.env.user.id,
            'reviewed_at': fields.Datetime.now(),
        })
        if not self.opened_at:
            self.opened_at = fields.Datetime.now()

    def action_approve(self):
        """Approve report and sync to linked agenda item."""
        self.ensure_one()
        vals = {
            'status': 'approved',
            'approved_at': fields.Datetime.now(),
        }
        self.write(vals)
        # Auto-sync to agenda item if linked
        if self.agenda_item_id:
            final_content = self.edited_content or self.content
            self.agenda_item_id.write({
                'notes': final_content,
                'ai_generated': True,
                'report_status': 'approved',
            })

    def action_regenerate(self):
        """Request AI to regenerate the report."""
        self.ensure_one()
        self.write({
            'version': self.version + 1,
            'edit_distance': 'regenerated',
            'status': 'draft',
            'edited_content': False,
        })
        # Trigger regeneration via cron or quest — content set externally
        return True

    def open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'strategy.department.report',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # -- Nudge helpers ----------------------------------------------------
    def _nudge_social_proof_review(self):
        """Check how many department heads have reviewed this week's reports.
        Returns fraction string for social proof nudging, e.g. '3 av 4'."""
        this_week = self.search([
            ('week_start', '=', self.week_start),
        ])
        total = len(this_week)
        reviewed = len(this_week.filtered(
            lambda r: r.status in ('reviewed', 'approved')))
        return '%d av %d' % (reviewed, total) if total else '0 av 0'

    def _nudge_log(self, nudge_type, opened=False, converted=False):
        """Log a nudge event for later aggregation in kaizen.
        Stores in a simple format that kaizen can read."""
        _logger.info(
            'NUDGE: type=%s dept=%s opened=%s converted=%s',
            nudge_type, self.department_id.name, opened, converted)
        # Store in kaizen-report nudge_metrics when available (Fas 6)
        return True
    @api.model
    def cron_weekly_generate_reports(self):
        """Generate a department report for every active department.
        Runs Friday 16:00. Creates reports with status='draft'.
        Content is generated via LLM in a separate step (Meeting Prep quest)."""
        today = date.today()
        # Find this week's Monday
        week_start = today - timedelta(days=today.weekday())

        created = 0
        departments = self.env['hr.department'].search([('active', '=', True)])
        for dept in departments:
            # Skip if already generated this week
            existing = self.search([
                ('department_id', '=', dept.id),
                ('week_start', '=', week_start),
            ], limit=1)
            if existing:
                continue

            report = self.create({
                'department_id': dept.id,
                'week_start': week_start,
                'status': 'draft',
                'version': 1,
                'ai_generated': True,
            })

            # Post in department's Discuss channel if available
            if dept.discuss_channel_id:
                msg = report.message_post(
                    body=_('📊 Veckans avdelningsrapport är klar för granskning. '
                           '[Öppna rapport](%s)') % report.open_form()['res_id'],
                    message_type='notification',
                )
                report.discuss_channel_id = dept.discuss_channel_id
                report.discuss_message_id = msg

            # Notify department head via activity
            if dept.manager_id and dept.manager_id.user_id:
                report.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=dept.manager_id.user_id.id,
                    note=_('Granska veckans avdelningsrapport inför ledningsgruppsmötet.'),
                )

            created += 1

        _logger.info(
            'Department reports: generated %d reports for week %s',
            created, week_start.isoformat())
        return created
