# -*- coding: utf-8 -*-
"""Bridge: business.model.canvas → ai.quest.powerbox() → generated BMC."""

import logging
from odoo import models, _

_logger = logging.getLogger(__name__)


class BusinessModelCanvas(models.Model):
    _inherit = 'business.model.canvas'

    def action_generate_bmc(self):
        """Generate a complete BMC using the Strategy Composer AI quest."""
        self.ensure_one()

        quest = self.env['ai.quest'].search([
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

        prompt = (
            'Generate a complete 9-block Business Model Canvas for this company. '
            'Use get_live_context() for real Odoo data. '
            'Write each block to the corresponding Html field on the record. '
            'After generating, challenge 3 hidden assumptions and stress-test them.'
        )

        try:
            result = quest.powerbox(
                prompt=prompt,
                res_model=self._name,
                res_id=self.id,
            )
            self.message_post(body=_('AI-generated BMC completed.'))

        except Exception as e:
            _logger.error('BMC generation failed: %s', e, exc_info=True)
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
                'title': _('BMC Generated'),
                'message': _('Review the 9 blocks and validate when ready.'),
                'type': 'success',
            }
        }

    def action_stress_test_bmc(self):
        """Stress-test the BMC assumptions."""
        self.ensure_one()

        quest = self.env['ai.quest'].search([
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

        prompt = (
            'Stress-test this Business Model Canvas. '
            'For each of the 9 blocks, identify the most critical assumption. '
            'For each assumption: what if it is wrong? How does the model break? '
            'What early warning signs would indicate the assumption is failing? '
            'Write findings as comments or linked risk records.'
        )

        try:
            quest.powerbox(
                prompt=prompt,
                res_model=self._name,
                res_id=self.id,
            )
            self.message_post(body=_('BMC stress-test completed.'))

        except Exception as e:
            _logger.error('BMC stress-test failed: %s', e, exc_info=True)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Stress-Test Complete'),
                'message': _('Review findings in the chatter.'),
                'type': 'success',
            }
        }
