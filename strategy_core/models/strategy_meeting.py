# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StrategyMeeting(models.Model):
    """Board and management meetings — the execution engine for strategy.
    Links to calendar.event for scheduling and contains agenda, decisions,
    participants, and minutes."""

    _name = 'strategy.meeting'
    _description = 'Strategic Meeting'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, name'

    # -- Identity ----------------------------------------------------------
    name = fields.Char('Meeting Title', required=True, tracking=True)
    meeting_type = fields.Selection([
        ('board', 'Board of Directors'),
        ('management', 'Management Team'),
    ], string='Meeting Type', required=True, default='management', tracking=True)

    # -- Time & Place ------------------------------------------------------
    calendar_event_id = fields.Many2one(
        'calendar.event', 'Calendar Event',
        ondelete='set null', tracking=True,
        help="Linked calendar event for scheduling, invitations, and reminders")

    date = fields.Datetime(
        'Meeting Date', related='calendar_event_id.start', readonly=False,
        store=False,
        help="Date and time from the linked calendar event")

    # -- Strategy context --------------------------------------------------
    plan_id = fields.Many2one(
        'strategy.plan', 'Strategic Plan',
        ondelete='set null', tracking=True,
        help="The strategic plan this meeting discusses")
    customer_id = fields.Many2one(
        'res.partner', 'Customer',
        related='plan_id.customer_id', store=True)

    # -- Agenda ------------------------------------------------------------
    agenda_item_ids = fields.One2many(
        'strategy.meeting.agenda.item', 'meeting_id',
        string='Agenda Items', copy=True)

    # -- Participants ------------------------------------------------------
    participant_ids = fields.One2many(
        'strategy.meeting.participant', 'meeting_id',
        string='Participants')

    participant_count = fields.Integer(
        'Participants', compute='_compute_participant_count')

    # -- Decisions ---------------------------------------------------------
    decision_ids = fields.One2many(
        'strategy.meeting.decision', 'meeting_id',
        string='Decisions')

    # -- Minutes -----------------------------------------------------------
    minutes_html = fields.Html('Minutes')
    minutes_draft = fields.Html('Minutes (Draft)',
        help="AI-generated draft minutes, editable before finalizing")

    # -- State -------------------------------------------------------------
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('adjourned', 'Adjourned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='scheduled', required=True, tracking=True)

    # -- Template ----------------------------------------------------------
    template_id = fields.Many2one(
        'strategy.meeting.template', 'Meeting Template',
        help="Template used to generate this meeting's agenda")

    # -- Metadata ----------------------------------------------------------
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company)
    user_id = fields.Many2one(
        'res.users', 'Organizer',
        default=lambda self: self.env.user, tracking=True)

    # -- Computed ----------------------------------------------------------
    @api.depends('participant_ids')
    def _compute_participant_count(self):
        for meeting in self:
            meeting.participant_count = len(meeting.participant_ids)

    # -- Actions -----------------------------------------------------------
    def action_start(self):
        self.write({'state': 'in_progress'})
        return True

    def action_complete(self):
        self.write({'state': 'completed'})
        return True

    # -- Calendar integration ---------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        meetings = super().create(vals_list)
        for meeting in meetings:
            try:
                meeting._auto_create_calendar_event()
                meeting._sync_participants_to_calendar()
            except Exception:
                _logger.warning(
                    'Calendar event creation failed for meeting %s',
                    meeting.id, exc_info=True)
        return meetings

    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ('name', 'user_id', 'meeting_type')):
            for meeting in self:
                if meeting.calendar_event_id:
                    meeting._update_calendar_event()
        return res

    def _auto_create_calendar_event(self):
        """Create calendar event automatically on meeting creation."""
        self.ensure_one()
        if self.calendar_event_id:
            return
        duration_hours = 2.0  # Default 2 hours
        if self.meeting_type == 'board':
            duration_hours = 3.0  # Board meetings typically longer
        alarm_type = self.env.ref(
            'calendar.mail_alarm_reminder_1day', raise_if_not_found=False) \
            if self.meeting_type == 'board' else self.env.ref(
            'calendar.mail_alarm_reminder_1hour', raise_if_not_found=False)
        alarm_ids = [(4, alarm_type.id)] if alarm_type else []
        event = self.env['calendar.event'].create({
            'name': self.name,
            'description': 'Strategy Meeting — %s\n\nPlan: %s' % (
                dict(self._fields['meeting_type'].selection).get(
                    self.meeting_type, ''),
                self.plan_id.display_name if self.plan_id else 'N/A'),
            'user_id': self.user_id.id,
            'allday': False,
            'duration': duration_hours,
            'alarm_ids': alarm_ids,
        })
        self.calendar_event_id = event.id

    def _update_calendar_event(self):
        """Sync meeting fields to linked calendar event."""
        self.ensure_one()
        if not self.calendar_event_id:
            return
        self.calendar_event_id.write({
            'name': self.name,
            'description': 'Strategy Meeting — %s\n\nPlan: %s' % (
                dict(self._fields['meeting_type'].selection).get(
                    self.meeting_type, ''),
                self.plan_id.display_name if self.plan_id else 'N/A'),
        })

    def _sync_participants_to_calendar(self):
        """Sync meeting participants to calendar event attendees."""
        self.ensure_one()
        if not self.calendar_event_id:
            return
        event = self.calendar_event_id
        for participant in self.participant_ids:
            employee = participant.employee_id
            if employee.user_id:
                existing = event.attendee_ids.filtered(
                    lambda a: a.partner_id == employee.user_id.partner_id)
                if not existing:
                    self.env['calendar.attendee'].create({
                        'event_id': event.id,
                        'partner_id': employee.user_id.partner_id.id,
                    })
            elif employee.work_email:
                # Create attendee with email for external participants
                existing = event.attendee_ids.filtered(
                    lambda a: a.email == employee.work_email)
                if not existing:
                    self.env['calendar.attendee'].create({
                        'event_id': event.id,
                        'email': employee.work_email,
                        'display_name': employee.name,
                    })

    def action_create_calendar_event(self):
        """Manually create or update the linked calendar event."""
        self.ensure_one()
        self._auto_create_calendar_event()
        self._sync_participants_to_calendar()
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        if self.calendar_event_id:
            try:
                self.calendar_event_id.action_cancel()
            except Exception:
                _logger.warning(
                    'Failed to cancel calendar event %s',
                    self.calendar_event_id.id, exc_info=True)
        return True

    def action_draft(self):
        self.write({'state': 'scheduled'})
        return True

    def action_apply_template(self):
        """Apply the selected template to generate agenda items."""
        self.ensure_one()
        if not self.template_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Template'),
                    'message': _('Select a meeting template first.'),
                    'type': 'warning',
                }
            }
        self.template_id.apply(self)
        return True

    def action_auto_compose_participants(self):
        """Auto-compose participants based on meeting type."""
        self.ensure_one()
        domain = []
        if self.meeting_type == 'board':
            domain = [('is_board_member', '=', True)]
        elif self.meeting_type == 'management':
            domain = [('is_management_team', '=', True)]

        employees = self.env['hr.employee'].search(domain)
        for emp in employees:
            role = 'member'
            if self.meeting_type == 'board' and emp.board_role == 'chairman':
                role = 'chairman'
            elif self.meeting_type == 'board' and emp.board_role == 'vice_chairman':
                role = 'vice_chairman'
            self.env['strategy.meeting.participant'].create({
                'meeting_id': self.id,
                'employee_id': emp.id,
                'role': role,
            })
        return True

    def open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'strategy.meeting',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }


class StrategyMeetingAgendaItem(models.Model):
    """A single point on a meeting agenda with timing, owner, and
    supporting documents."""

    _name = 'strategy.meeting.agenda.item'
    _description = 'Meeting Agenda Item'
    _order = 'sequence, id'

    sequence = fields.Integer('Order', default=10)
    name = fields.Char('Agenda Item', required=True)
    meeting_id = fields.Many2one(
        'strategy.meeting', 'Meeting',
        required=True, ondelete='cascade')
    duration_minutes = fields.Integer('Duration (min)', default=15)
    user_id = fields.Many2one(
        'res.users', 'Responsible')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('current', 'Current'),
        ('done', 'Done'),
    ], string='Status', default='pending')
    notes = fields.Html('Notes',
        help="AI-generated brief or live meeting notes")
    document_ids = fields.Many2many(
        'ir.attachment', 'meeting_agenda_attachment_rel',
        'agenda_id', 'attachment_id',
        string='Documents')
    source = fields.Selection([
        ('manual', 'Manual'),
        ('ai_suggested', 'AI Suggested'),
        ('template', 'From Template'),
    ], string='Source', default='manual')

    # -- Department linkage (strategy-nudge-engine) --
    department_id = fields.Many2one(
        'hr.department', 'Department',
        help='Department that reports on this agenda item. '
             'When set, Meeting Prep quest generates department-specific content.')
    item_type = fields.Selection([
        ('standard', 'Standard'),
        ('department_report', 'Department Report'),
        ('strategic_status', 'Strategic Status'),
    ], string='Item Type', default='standard')
    report_status = fields.Selection([
        ('draft', 'AI Draft'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
    ], string='Report Status', default='draft')
    ai_generated = fields.Boolean('AI Generated', default=False)


class StrategyMeetingParticipant(models.Model):
    """A meeting attendee with role and status."""

    _name = 'strategy.meeting.participant'
    _description = 'Meeting Participant'
    _order = 'role, employee_id'

    meeting_id = fields.Many2one(
        'strategy.meeting', 'Meeting',
        required=True, ondelete='cascade')
    employee_id = fields.Many2one(
        'hr.employee', 'Participant',
        required=True, ondelete='restrict')
    role = fields.Selection([
        ('chairman', 'Chairman'),
        ('vice_chairman', 'Vice Chairman'),
        ('member', 'Member'),
        ('adjungated', 'Adjungated'),
        ('secretary', 'Secretary'),
        ('guest', 'Guest'),
    ], string='Role', default='member')
    attended = fields.Boolean('Attended', default=False)
    rsvp_status = fields.Selection([
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ], string='RSVP', default='pending')

    _sql_constraints = [
        ('meeting_employee_unique',
         'UNIQUE(meeting_id, employee_id)',
         'Each employee can only be a participant once per meeting.'),
    ]


class StrategyMeetingDecision(models.Model):
    """A decision made during a meeting, optionally linked to a strategy
    model (risk, OKR, initiative, plan) via generic reference."""

    _name = 'strategy.meeting.decision'
    _description = 'Meeting Decision'
    _order = 'create_date desc, id'

    name = fields.Char('Decision', required=True)
    description = fields.Text('Description')
    meeting_id = fields.Many2one(
        'strategy.meeting', 'Meeting',
        required=True, ondelete='cascade')
    agenda_item_id = fields.Many2one(
        'strategy.meeting.agenda.item', 'Agenda Item',
        ondelete='set null')
    state = fields.Selection([
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
    ], string='Status', default='proposed')

    # Generic reference to any strategy model
    res_model = fields.Char('Related Model', index=True)
    res_id = fields.Integer('Related Record ID')
    ref_display_name = fields.Char('Reference', compute='_compute_ref_display_name')

    user_id = fields.Many2one(
        'res.users', 'Responsible',
        default=lambda self: self.env.user)

    # -- Nudge ladder fields (strategy-nudge-engine) --
    deadline = fields.Date('Deadline')
    implemented = fields.Boolean('Implemented', default=False)
    implemented_at = fields.Datetime('Implemented At')
    nudge_level = fields.Integer('Nudge Level', default=0,
        help='0=not nudged, 1=day3 prompt, 2=day7 social proof, '
             '3=day14 agenda, 4=day30 escalation')
    nudge_opt_out = fields.Boolean('Nudge Paused', default=False,
        help='Owner has requested "pågår — påminn mig senare". '
             'Pauses the nudge ladder.')
    last_nudge_at = fields.Datetime('Last Nudge')

    @api.depends('res_model', 'res_id')
    def _compute_ref_display_name(self):
        for decision in self:
            if decision.res_model and decision.res_id:
                try:
                    record = self.env[decision.res_model].browse(decision.res_id)
                    decision.ref_display_name = record.display_name
                except Exception:
                    decision.ref_display_name = '%s #%s' % (
                        decision.res_model, decision.res_id)
            else:
                decision.ref_display_name = False

    def action_approve(self):
        self.write({'state': 'approved'})
        for decision in self:
            if decision.deadline and decision.user_id:
                decision._suggest_implementation_intention()
        return True

    def _suggest_implementation_intention(self):
        """Generate an if-then plan suggestion for the decision owner.
        Based on Gollwitzer (1999): 'When X, then Y' plans dramatically
        increase follow-through by pre-committing to a trigger."""
        self.ensure_one()
        if not self.user_id or not self.deadline:
            return
        weekday = self.deadline.strftime('%A')
        self.meeting_id.message_post(
            body=_('💡 **Implementation intention:**\n'
                   '"När klockan är 09:00 på %s, '
                   'påbörja arbetet med beslutet: %s"\n\n'
                   '<em>Forskning visar att när-så-planer ökar '
                   'sannolikheten att genomföra målet. '
                   'Detta är ett AI-förslag — anpassa tid och dag '
                   'som du vill.</em>') % (weekday, self.name),
            message_type='notification',
            partner_ids=[self.user_id.partner_id.id],
        )

    def action_reject(self):
        self.write({'state': 'rejected'})
        return True

    def action_defer(self):
        self.write({'state': 'deferred'})
        return True

    def action_implemented(self):
        self.write({
            'implemented': True,
            'implemented_at': fields.Datetime.now(),
            'nudge_level': 0,
        })
        return True

    def action_pause_nudge(self):
        """Opt out of nudging — 'pågår, påminn mig senare'."""
        self.write({'nudge_opt_out': True})
        return True

    def action_resume_nudge(self):
        self.write({'nudge_opt_out': False})
        return True

    @api.model
    def cron_nudge_ladder(self):
        """Daily cron: escalate nudge levels for open approved decisions.
        Implements the nudge ladder:
        Day 3 → prompt, Day 7 → social proof, Day 14 → agenda, Day 30 → escalate."""
        today = date.today()
        decisions = self.search([
            ('state', '=', 'approved'),
            ('implemented', '=', False),
            ('nudge_opt_out', '=', False),
        ])

        for dec in decisions:
            if not dec.deadline:
                continue
            days_open = (today - dec.deadline).days

            if days_open >= 30 and dec.nudge_level < 4:
                # Day 30: Escalation to department head + meeting chair
                dec._nudge_escalate()
                dec.write({'nudge_level': 4, 'last_nudge_at': fields.Datetime.now()})
            elif days_open >= 14 and dec.nudge_level < 3:
                # Day 14: Auto-add to next meeting agenda
                dec._nudge_add_to_agenda()
                dec.write({'nudge_level': 3, 'last_nudge_at': fields.Datetime.now()})
            elif days_open >= 7 and dec.nudge_level < 2:
                # Day 7: Social proof
                dec._nudge_social_proof()
                dec.write({'nudge_level': 2, 'last_nudge_at': fields.Datetime.now()})
            elif days_open >= 3 and dec.nudge_level < 1:
                # Day 3: Prompt
                dec._nudge_prompt()
                dec.write({'nudge_level': 1, 'last_nudge_at': fields.Datetime.now()})

        _logger.info('Nudge ladder: processed %d decisions', len(decisions))
        return True

    def _nudge_prompt(self):
        """Day 3: Simple prompt in quest chat."""
        self.ensure_one()
        if self.user_id:
            self.meeting_id.message_post(
                body=_('⏳ Påminnelse: Beslut "%s" från %s väntar på åtgärd. '
                       'Ansvarig: %s') % (
                    self.name, self.meeting_id.name, self.user_id.name),
                message_type='notification',
                partner_ids=[self.user_id.partner_id.id],
            )

    def _nudge_social_proof(self):
        """Day 7: Social proof — how many decisions implemented."""
        self.ensure_one()
        meeting_decisions = self.search([
            ('meeting_id', '=', self.meeting_id.id),
            ('state', '=', 'approved'),
        ])
        total = len(meeting_decisions)
        implemented = len(meeting_decisions.filtered('implemented'))
        pct = int(implemented / total * 100) if total else 0

        if self.user_id:
            self.meeting_id.message_post(
                body=_('📊 %d%% av besluten från %s har verkställts '
                       '(%d av %d). Ditt beslut "%s" är ännu inte påbörjat.') % (
                    pct, self.meeting_id.name, implemented, total, self.name),
                message_type='notification',
                partner_ids=[self.user_id.partner_id.id],
            )

    def _nudge_add_to_agenda(self):
        """Day 14: Auto-add open decision to next meeting's agenda."""
        self.ensure_one()
        # Find the next meeting of the same type
        next_meeting = self.env['strategy.meeting'].search([
            ('meeting_type', '=', self.meeting_id.meeting_type),
            ('state', '=', 'scheduled'),
            ('id', '!=', self.meeting_id.id),
        ], order='create_date asc', limit=1)

        if next_meeting:
            self.env['strategy.meeting.agenda.item'].create({
                'meeting_id': next_meeting.id,
                'name': 'Uppföljning: %s' % self.name,
                'duration_minutes': 5,
                'notes': '<p><strong>Ej verkställt beslut från %s:</strong> %s</p>'
                         '<p>Ansvarig: %s | Deadline: %s</p>' % (
                    self.meeting_id.name, self.description or self.name,
                    self.user_id.name if self.user_id else '-',
                    self.deadline.isoformat() if self.deadline else '-'),
                'source': 'ai_suggested',
            })

    def _nudge_escalate(self):
        """Day 30: Escalate to department head and meeting chair."""
        self.ensure_one()
        # Notify meeting organizer
        if self.meeting_id.user_id:
            self.meeting_id.message_post(
                body=_('🚨 ESKALERING: Beslut "%s" från %s är 30 dagar '
                       'gammalt och ej verkställt. Ansvarig: %s.') % (
                    self.name, self.meeting_id.name,
                    self.user_id.name if self.user_id else 'okänd'),
                message_type='notification',
                partner_ids=[self.meeting_id.user_id.partner_id.id],
            )


class StrategyMeetingTemplate(models.Model):
    """Reusable meeting template with predefined agenda items."""

    _name = 'strategy.meeting.template'
    _description = 'Meeting Template'
    _order = 'name'

    name = fields.Char('Template Name', required=True)
    meeting_type = fields.Selection([
        ('board', 'Board of Directors'),
        ('management', 'Management Team'),
    ], string='Meeting Type', required=True)
    line_ids = fields.One2many(
        'strategy.meeting.template.line', 'template_id',
        string='Agenda Items', copy=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company)

    def apply(self, meeting):
        """Apply this template to a meeting, creating agenda items.
        For department_report items without a specific department,
        auto-creates one item per active department."""
        meeting.agenda_item_ids.unlink()
        for line in self.line_ids.sorted('sequence'):
            if line.item_type == 'department_report' and not line.department_id:
                # Auto-create one agenda item per active department
                departments = self.env['hr.department'].search([
                    ('active', '=', True),
                ])
                for i, dept in enumerate(departments):
                    self.env['strategy.meeting.agenda.item'].create({
                        'meeting_id': meeting.id,
                        'sequence': line.sequence + i,
                        'name': '%s — %s' % (line.name, dept.name),
                        'duration_minutes': line.duration_minutes,
                        'item_type': 'department_report',
                        'department_id': dept.id,
                        'source': 'template',
                    })
            else:
                vals = {
                    'meeting_id': meeting.id,
                    'sequence': line.sequence,
                    'name': line.name,
                    'duration_minutes': line.duration_minutes,
                    'item_type': line.item_type,
                    'source': 'template',
                }
                if line.department_id:
                    vals['department_id'] = line.department_id.id
                self.env['strategy.meeting.agenda.item'].create(vals)


class StrategyMeetingTemplateLine(models.Model):
    """A predefined agenda item within a meeting template."""

    _name = 'strategy.meeting.template.line'
    _description = 'Meeting Template Line'
    _order = 'sequence, id'

    sequence = fields.Integer('Order', default=10)
    name = fields.Char('Agenda Item', required=True)
    duration_minutes = fields.Integer('Duration (min)', default=15)
    item_type = fields.Selection([
        ('standard', 'Standard'),
        ('department_report', 'Department Report'),
        ('strategic_status', 'Strategic Status'),
    ], string='Item Type', default='standard')
    department_id = fields.Many2one(
        'hr.department', 'Department',
        help='For department_report items: which department reports. '
             'Leave empty to auto-create for all active departments.')
    template_id = fields.Many2one(
        'strategy.meeting.template', 'Template',
        required=True, ondelete='cascade')
