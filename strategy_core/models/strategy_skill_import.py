# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
import yaml
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class StrategySkillImport(models.TransientModel):
    _name = 'strategy.skill.import'
    _description = 'Import Strategy Skills from SKILL.md files'

    def action_import(self):
        """Scan skills/ directory and import all SKILL.md files into
        marketing.skill records."""
        skills_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'skills'
        )

        if not os.path.isdir(skills_dir):
            _logger.warning('Skills directory not found: %s', skills_dir)
            return {'type': 'ir.actions.act_window_close'}

        imported = 0
        updated = 0

        for skill_name in sorted(os.listdir(skills_dir)):
            skill_path = os.path.join(skills_dir, skill_name, 'SKILL.md')
            if not os.path.isfile(skill_path):
                continue

            try:
                frontmatter, body = self._parse_skill_md(skill_path)
            except Exception as e:
                _logger.warning('Failed to parse %s: %s', skill_path, e)
                continue

            name = frontmatter.get('name', skill_name)
            existing = self.env['marketing.skill'].search([
                ('name', '=', name)
            ], limit=1)

            vals = {
                'name': name,
                'description': frontmatter.get('description', ''),
                'category': 'strategy',
                'version': (frontmatter.get('metadata') or {}).get('version', '1.0.0'),
                'skill_content': body,
                'skill_path': 'skills/%s/SKILL.md' % skill_name,
                'is_base': True,
                'is_active': True,
            }

            if existing:
                existing.write(vals)
                updated += 1
            else:
                self.env['marketing.skill'].create(vals)
                imported += 1

        _logger.info(
            'Strategy skill import complete: %d imported, %d updated',
            imported, updated
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Skills Imported'),
                'message': _('%d new, %d updated') % (imported, updated),
                'type': 'success',
            },
        }

    def _parse_skill_md(self, path):
        """Parse SKILL.md with YAML frontmatter."""
        with open(path, 'r') as f:
            content = f.read()

        # Extract YAML frontmatter between --- markers
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
                return frontmatter, body

        # No frontmatter — treat entire file as body
        return {}, content.strip()
