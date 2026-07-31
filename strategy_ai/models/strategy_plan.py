# -*- coding: utf-8 -*-
"""Bridge: strategy.plan → ai.coworker.powerbox() → generated business plan."""

import logging
from odoo import models, _

_logger = logging.getLogger(__name__)


class StrategyPlan(models.Model):
    _inherit = 'strategy.plan'

    def action_generate_business_plan(self):
        """Generate a full business plan using the Strategy Composer AI quest.

        Finds the powerbox quest from ai_agent_core_strategy, passes this
        plan as context, and writes the result to plan.description.
        """
        self.ensure_one()

        quest = self.env['ai.coworker'].search([
            ('init_type', '=', 'powerbox'),
            ('name', '=', 'Strategy Composer'),
        ], limit=1)

        if not quest:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Strategy Composer not found'),
                    'message': _(
                        'The ai_agent_core_strategy module must be installed '
                        'to use AI features.'),
                    'type': 'warning',
                }
            }

        # Build audience-aware prompt
        audience = self.target_audience or 'internal'
        audience_prompts = {
            'internal': (
                'Generate a concise internal strategic plan. '
                'Focus on team alignment, operational details, and clear action items. '
                'Language: Swedish if company is Swedish, otherwise English. '
                'Target: 5-10 pages equivalent.'
            ),
            'investor': (
                'Generate an investor pitch business plan. '
                'Emphasize market opportunity, growth trajectory, competitive advantage, '
                'and financial projections. Language: English. '
                'Target: 10-15 slides equivalent. Include an executive summary.'
            ),
            'bank': (
                'Generate a bank loan application business plan. '
                'Emphasize financial stability, cash flow analysis, collateral, '
                'repayment capacity, and risk mitigation. '
                'Include detailed financial sections. Language: Swedish.'
            ),
            'board': (
                'Generate a board of directors strategic overview. '
                'Concise executive summary, key metrics, strategic priorities, '
                'major risks, and decisions required. '
                'Target: 3-5 pages equivalent. Language: Swedish.'
            ),
        }

        prompt = audience_prompts.get(audience, audience_prompts['internal'])
        prompt += (
            '\n\nContext: This plan covers the period %s to %s. '
            'The company is %s.'
        ) % (
            self.date_from or 'TBD',
            self.date_to or 'TBD',
            self.customer_id.name if self.customer_id else self.company_id.name,
        )

        try:
            result = quest.powerbox(
                prompt=prompt,
                res_model=self._name,
                res_id=self.id,
            )

            if result:
                self.write({'description': result})
                self.message_post(
                    body=_(
                        'AI-generated business plan (audience: %s). '
                        'Review and edit as needed.') % dict(
                            self._fields['target_audience'].selection
                        ).get(audience, audience)
                )

        except Exception as e:
            _logger.error('Business plan generation failed: %s', e, exc_info=True)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Generation Failed'),
                    'message': str(e)[:200],
                    'type': 'danger',
                }
            }

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Business Plan Generated'),
                'message': _(
                    'The AI has generated a draft business plan. '
                    'Review the Executive Summary field and edit as needed.'),
                'type': 'success',
            }
        }

    def action_improve_business_plan(self):
        """Ask the AI to review and improve the existing business plan."""
        self.ensure_one()

        if not self.description:
            return self.action_generate_business_plan()

        quest = self.env['ai.coworker'].search([
            ('init_type', '=', 'powerbox'),
            ('name', '=', 'Strategy Composer'),
        ], limit=1)

        if not quest:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Not Available'),
                    'message': _('Strategy Composer quest not found.'),
                    'type': 'warning',
                }
            }

        audience = self.target_audience or 'internal'
        prompt = (
            'Review and improve this existing business plan. '
            'Keep the same audience focus (%s). '
            'Strengthen weak sections, add missing details, '
            'update any outdated information. '
            'Current plan content follows.'
        ) % audience

        try:
            result = quest.powerbox(
                prompt=prompt,
                res_model=self._name,
                res_id=self.id,
            )

            if result:
                self.write({'description': result})
                self.message_post(body=_('AI-improved business plan.'))

        except Exception as e:
            _logger.error('Plan improvement failed: %s', e, exc_info=True)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Plan Improved'),
                'message': _('The AI has improved the business plan.'),
                'type': 'success',
            }
        }
