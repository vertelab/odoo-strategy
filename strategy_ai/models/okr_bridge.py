# -*- coding: utf-8 -*-
"""OKR → ai.org.goal bridge.

Kopplar okr.objective → ai.org.goal och okr.key.result → ai.org.key.result
idempotent (utan dubbletter vid re-run). AI-målmodellen (ai.org.goal) ligger
i ai_agent_core; denna bridge skapar speglade mål för AI-orchestrering.

Idempotens: vi söker på ai.org.goal.external_ref (polymorf Reference) —
finns målposten redan uppdateras den, annars skapas den.
"""

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AIOrgGoal(models.Model):
    _inherit = 'ai.org.goal'

    @api.model
    def _selection_external_refs(self):
        """Lägg till okr.objective som extern referenskälla."""
        return super()._selection_external_refs() + [
            ('okr.objective', 'OKR Objective'),
        ]


class OkrObjective(models.Model):
    _inherit = 'okr.objective'

    ai_goal_id = fields.Many2one(
        'ai.org.goal', string='AI Goal (bridge)', readonly=True,
        help='Speglad ai.org.goal skapad av strategy_ai-bryggan.')

    def action_sync_ai_goal(self):
        """Skapa/uppdatera speglad ai.org.goal för markerade OKR:er."""
        for obj in self:
            self._sync_ai_org_goal(obj)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI-mål synkade'),
                'message': _('%s OKR:er synkade till ai.org.goal.'
                             % len(self)),
                'type': 'success',
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            try:
                self._sync_ai_org_goal(rec)
            except Exception as e:
                _logger.warning('OKR→ai.org.goal sync misslyckades: %s', e)
        return records

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            try:
                self._sync_ai_org_goal(rec)
            except Exception as e:
                _logger.warning('OKR→ai.org.goal sync misslyckades: %s', e)
        return res

    @api.model
    def _sync_ai_org_goal(self, okr):
        """Idempotent spegling av en okr.objective → ai.org.goal.

        Använder external_ref 'okr.objective,<id>' som nyckel — re-run
        uppdaterar istället för att duplicera.
        """
        ai_goal_model = self.env['ai.org.goal']
        external = 'okr.objective,%s' % okr.id

        goal = ai_goal_model.search([
            ('external_ref', '=', external),
        ], limit=1)

        vals = {
            'name': okr.name,
            'description': okr.description or '',
            'level': 'department' if okr.department_id else 'company',
            'department_id': okr.department_id.id,
            'status': {
                'draft': 'draft',
                'active': 'active',
                'achieved': 'completed',
                'cancelled': 'cancelled',
            }.get(okr.state, 'draft'),
            'external_ref': external,
        }

        if goal:
            goal.write(vals)
        else:
            goal = ai_goal_model.create(vals)
            okr.ai_goal_id = goal.id

        # ── Key results: spegla idempotent ──
        existing_krs = {
            kr.name: kr
            for kr in goal.key_result_ids
        }
        for kr in okr.key_result_ids:
            if kr.name in existing_krs:
                existing_krs[kr.name].write({
                    'target_value': kr.target_value,
                    'current_value': kr.current_value,
                    'unit': kr.unit or '%',
                })
            else:
                goal.key_result_ids = [(0, 0, {
                    'name': kr.name,
                    'target_value': kr.target_value,
                    'current_value': kr.current_value,
                    'unit': kr.unit or '%',
                })]

        # Ta bort KR:er som inte längre finns i källan (men behåll om
        # okr.key_result saknar name-match — enkel och säker strategi).
        return goal


class OkrKeyResult(models.Model):
    """Synka okr.key.result → ai.org.key.result via objective-bryggan."""
    _inherit = 'okr.key.result'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.objective_id:
                try:
                    rec.objective_id._sync_ai_org_goal(rec.objective_id)
                except Exception as e:
                    _logger.warning('KR→ai.org.key.result sync misslyckades: %s', e)
        return records

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.objective_id:
                try:
                    rec.objective_id._sync_ai_org_goal(rec.objective_id)
                except Exception as e:
                    _logger.warning('KR→ai.org.key.result sync misslyckades: %s', e)
        return res
