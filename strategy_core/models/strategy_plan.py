# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StrategyPlan(models.Model):
    """Top-level Strategic Plan — the central document that ties together
    all strategy artifacts: BMC, SWOT, VPC, OKRs, Vision docs, Initiatives,
    Risks, and Actions."""

    _name = 'strategy.plan'
    _description = 'Strategic Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, name'

    # -- Identity ----------------------------------------------------------
    name = fields.Char('Plan Name', required=True, tracking=True)
    customer_id = fields.Many2one(
        'res.partner', 'Customer',
        domain=[('customer_rank', '>', 0)],
        tracking=True)
    description = fields.Html('Executive Summary')

    # -- Timeframe ---------------------------------------------------------
    date_from = fields.Date('From', tracking=True,
        help="Start of the strategic period")
    date_to = fields.Date('To', tracking=True,
        help="End of the strategic period (typically 3-5 years)")

    # -- Audience ----------------------------------------------------------
    target_audience = fields.Selection([
        ('internal', 'Internal'),
        ('investor', 'Investor Pitch'),
        ('bank', 'Bank / Loan Application'),
        ('board', 'Board of Directors'),
    ], string='Target Audience', default='internal', tracking=True,
        help="Who will read this plan? Adapts AI-generated content "
             "accordingly (language, detail level, financial focus).")

    # -- Foundation documents ----------------------------------------------
    vision_ids = fields.One2many(
        'strategy.vision', 'plan_id',
        string='Vision, Mission & Values')
    bmc_ids = fields.One2many(
        'business.model.canvas', 'plan_id',
        string='Business Model Canvases')
    swot_ids = fields.One2many(
        'swot.analysis', 'plan_id',
        string='SWOT Analyses')
    vpc_ids = fields.One2many(
        'value.proposition.canvas', 'plan_id',
        string='Value Proposition Canvases')

    # -- Execution ---------------------------------------------------------
    objective_ids = fields.One2many(
        'okr.objective', 'plan_id',
        string='OKR Objectives')
    initiative_ids = fields.One2many(
        'strategy.initiative', 'plan_id',
        string='Strategic Initiatives')
    risk_ids = fields.One2many(
        'strategy.risk', 'plan_id',
        string='Strategic Risks')
    # NOTE: forecast_ids removed — strategy.forecast is in strategy_finance
    # (a dependent module loaded after strategy_core). The inverse
    # strategy.forecast.plan_id Many2one still works for linking.

    # -- Computed summary --------------------------------------------------
    total_initiatives = fields.Integer(
        'Initiatives', compute='_compute_summary')
    active_okrs = fields.Integer(
        'Active OKRs', compute='_compute_summary')
    total_risks = fields.Integer(
        'Risks', compute='_compute_summary')
    progress = fields.Float(
        'Overall Progress %', compute='_compute_progress', store=True)

    # -- State ------------------------------------------------------------
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('under_review', 'Under Review'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', required=True, tracking=True)

    # -- Metadata ----------------------------------------------------------
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company)
    user_id = fields.Many2one(
        'res.users', 'Owner',
        default=lambda self: self.env.user, tracking=True)
    approved_date = fields.Date('Approved Date')
    approved_by = fields.Many2one('res.users', 'Approved By')

    @api.depends('initiative_ids', 'objective_ids', 'risk_ids')
    def _compute_summary(self):
        for plan in self:
            plan.total_initiatives = len(plan.initiative_ids)
            plan.active_okrs = len(plan.objective_ids.filtered(
                lambda o: o.state == 'active'))
            plan.total_risks = len(plan.risk_ids)

    @api.depends('objective_ids.progress')
    def _compute_progress(self):
        for plan in self:
            objs = plan.objective_ids
            plan.progress = (
                sum(objs.mapped('progress')) / len(objs)
                if objs else 0.0
            )

    # -- Actions -----------------------------------------------------------
    def action_activate(self):
        self.write({'state': 'active'})
        return True

    def action_review(self):
        self.write({'state': 'under_review'})
        return True

    def action_complete(self):
        self.write({'state': 'completed'})
        return True

    def action_archive(self):
        self.write({'state': 'archived'})
        return True

    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_approve(self):
        """Approve the strategic plan."""
        self.write({
            'state': 'active',
            'approved_date': fields.Date.today(),
            'approved_by': self.env.user.id,
        })
        return True


class StrategyVision(models.Model):
    """Vision, Mission, Values and similar foundational strategy documents.
    Each document has a type and automatic version numbering that increments
    when the document is approved."""

    _name = 'strategy.vision'
    _description = 'Vision, Mission & Values Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, document_type, name'

    # -- Sequence (manual ordering) ---------------------------------------
    sequence = fields.Integer('Sequence', default=10,
        help="Drag to reorder in list view")

    # -- Identity ----------------------------------------------------------
    name = fields.Char('Title', required=True, tracking=True)
    document_type = fields.Selection([
        ('vision', 'Vision'),
        ('mission', 'Mission'),
        ('values', 'Core Values'),
        ('purpose', 'Purpose'),
        ('guiding_principles', 'Guiding Principles'),
        ('strategic_intent', 'Strategic Intent'),
        ('bhag', 'BHAG (Big Hairy Audacious Goal)'),
        ('other', 'Other'),
    ], string='Document Type', required=True, default='vision', tracking=True)
    plan_id = fields.Many2one(
        'strategy.plan', 'Strategic Plan',
        ondelete='cascade', tracking=True)
    customer_id = fields.Many2one(
        'res.partner', 'Customer', related='plan_id.customer_id', store=True)

    # -- Content -----------------------------------------------------------
    content = fields.Html('Content', sanitize=False)
    full_markdown = fields.Text('Full Content (Markdown)')
    generated_by = fields.Char('Generated By', default='pi-agent')

    # -- AI Enhancement ----------------------------------------------------
    ai_improved_content = fields.Html('AI Improved Content',
        help="AI-generated improved version of the content")
    ai_analysis = fields.Text('AI Analysis',
        help="AI-generated analysis and suggestions")
    ai_last_run = fields.Datetime('AI Last Run')

    # -- Versioning (automatic) --------------------------------------------
    major_version = fields.Integer(
        'Major Version', default=0,
        help="Auto-increments when document is approved")
    minor_version = fields.Integer(
        'Minor Version', default=1,
        help="Increments on draft edits; resets to 0 on approval")
    version = fields.Char(
        'Version', compute='_compute_version', store=True,
        help="Auto-generated: v{major}.{minor}")
    version_notes = fields.Text('Version Notes',
        help="Describe what changed in this version")
    approved_date = fields.Date('Approved Date')
    approved_by = fields.Many2one('res.users', 'Approved By')

    # -- State ------------------------------------------------------------
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_review', 'Under Review'),
        ('approved', 'Approved'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', required=True, tracking=True)

    # -- Metadata ----------------------------------------------------------
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company)
    user_id = fields.Many2one(
        'res.users', 'Owner',
        default=lambda self: self.env.user, tracking=True)

    @api.depends('major_version', 'minor_version')
    def _compute_version(self):
        for doc in self:
            doc.version = f'v{doc.major_version}.{doc.minor_version}'

    # -- Actions -----------------------------------------------------------
    def action_review(self):
        self.write({'state': 'in_review'})
        return True

    def action_draft(self):
        """Revert to draft for editing. Increments minor version if
        coming from approved state. From archived, simply unarchives."""
        self.ensure_one()
        vals = {'state': 'draft'}
        if self.state == 'approved':
            vals['minor_version'] = self.minor_version + 1
        self.write(vals)
        return True

    def action_approve(self):
        """Approve document. Auto-increments major version, resets minor."""
        self.ensure_one()
        if self.state not in ('draft', 'in_review'):
            raise UserError(_(
                'Only draft or in-review documents can be approved.'))
        self.write({
            'state': 'approved',
            'major_version': self.major_version + 1,
            'minor_version': 0,
            'approved_date': fields.Date.today(),
            'approved_by': self.env.user.id,
        })
        return True

    def action_archive(self):
        self.write({'state': 'archived'})
        return True

    # -- AI Actions --------------------------------------------------------
    def action_ai_improve(self):
        """Trigger AI to improve the document content.
        Saves result to ai_improved_content for review before applying."""
        self.ensure_one()
        # Placeholder for AI integration — replace with actual API call
        # The AI should read self.content and return improved version.
        # For now, log the intent and mark as pending.
        _logger.info(
            'AI improve requested for vision doc %s (id=%s, type=%s)',
            self.name, self.id, self.document_type)
        self.message_post(
            body=_('AI improvement requested for "%s".'),
            message_type='comment')
        return True

    def action_ai_analyze(self):
        """Trigger AI to analyze the document and provide suggestions."""
        self.ensure_one()
        _logger.info(
            'AI analysis requested for vision doc %s (id=%s)',
            self.name, self.id)
        self.message_post(
            body=_('AI analysis requested for "%s".'),
            message_type='comment')
        return True

    def action_ai_apply(self):
        """Apply the AI-improved content, replacing current content.
        Increments minor version."""
        self.ensure_one()
        if not self.ai_improved_content:
            raise UserError(_('No AI-improved content available. '
                            'Run "Improve with AI" first.'))
        self.write({
            'content': self.ai_improved_content,
            'ai_improved_content': False,
            'ai_last_run': False,
            'state': 'draft',
            'minor_version': self.minor_version + 1,
        })
        return True

    def action_ai_discard(self):
        """Discard the AI-improved content."""
        self.ensure_one()
        self.write({
            'ai_improved_content': False,
            'ai_last_run': False,
        })
        return True

    def open_form(self):
        """Open the vision document in form view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'strategy.vision',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure new documents start with major=0, minor=1."""
        for vals in vals_list:
            if 'major_version' not in vals:
                vals['major_version'] = 0
            if 'minor_version' not in vals:
                vals['minor_version'] = 1
        return super().create(vals_list)


class StrategyInitiative(models.Model):
    """Strategic Initiative — a project or program that drives OKR objectives.
    Has timeline, budget, ownership, and links to actions and risks."""

    _name = 'strategy.initiative'
    _description = 'Strategic Initiative'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # -- Identity ----------------------------------------------------------
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Initiative', required=True, tracking=True)
    plan_id = fields.Many2one(
        'strategy.plan', 'Strategic Plan',
        required=True, ondelete='cascade', tracking=True)
    customer_id = fields.Many2one(
        'res.partner', 'Customer', related='plan_id.customer_id', store=True)

    # -- Execution ---------------------------------------------------------
    objective_ids = fields.Many2many(
        'okr.objective', 'strategy_initiative_okr_rel',
        'initiative_id', 'objective_id',
        string='OKR Objectives',
        help="Which OKR objectives does this initiative drive?")
    owner_id = fields.Many2one(
        'res.users', 'Owner', tracking=True,
        default=lambda self: self.env.user)
    team_ids = fields.Many2many(
        'res.users', 'strategy_initiative_team_rel',
        'initiative_id', 'user_id',
        string='Team Members')

    # -- Timeline ----------------------------------------------------------
    date_start = fields.Date('Start Date', tracking=True)
    date_end = fields.Date('End Date', tracking=True)

    # -- Budget ------------------------------------------------------------
    budget = fields.Monetary('Budget', currency_field='currency_id')
    spent = fields.Monetary('Spent', currency_field='currency_id')
    budget_remaining = fields.Monetary(
        'Remaining', currency_field='currency_id',
        compute='_compute_budget', store=True)

    # -- Progress ----------------------------------------------------------
    progress = fields.Float(
        'Progress %', compute='_compute_progress', store=True,
        group_operator='avg')
    manual_progress = fields.Float(
        'Manual Progress %',
        help="Override progress when not using OKR-driven calculation")

    # -- Content -----------------------------------------------------------
    description = fields.Html('Description')
    success_criteria = fields.Html('Success Criteria')
    deliverables = fields.Html('Key Deliverables')
    dependencies = fields.Html('Dependencies & Constraints')

    # -- Related artifacts -------------------------------------------------
    action_ids = fields.One2many(
        'strategy.action', 'initiative_id',
        string='Actions')
    risk_ids = fields.One2many(
        'strategy.risk', 'initiative_id',
        string='Risks')

    # -- State ------------------------------------------------------------
    state = fields.Selection([
        ('proposed', 'Proposed'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('at_risk', 'At Risk'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='proposed', required=True, tracking=True)

    # -- Metadata ----------------------------------------------------------
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.depends('budget', 'spent')
    def _compute_budget(self):
        for ini in self:
            ini.budget_remaining = ini.budget - ini.spent

    @api.depends('objective_ids.progress', 'manual_progress')
    def _compute_progress(self):
        for ini in self:
            if ini.manual_progress:
                ini.progress = ini.manual_progress
            else:
                objs = ini.objective_ids
                ini.progress = (
                    sum(objs.mapped('progress')) / len(objs)
                    if objs else 0.0
                )

    # -- Actions -----------------------------------------------------------
    def action_approve(self):
        self.write({'state': 'approved'})
        return True

    def action_start(self):
        self.ensure_one()
        if not self.date_start:
            self.date_start = fields.Date.today()
        self.write({'state': 'in_progress'})
        return True

    def action_flag_risk(self):
        self.write({'state': 'at_risk'})
        return True

    def action_complete(self):
        self.write({
            'state': 'completed',
            'date_end': self.date_end or fields.Date.today(),
        })
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        return True

    def action_reopen(self):
        self.write({'state': 'in_progress'})
        return True

    def open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'strategy.initiative',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
