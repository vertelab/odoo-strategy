# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
import logging
import xml.sax.saxutils as saxutils

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StrategySkillSync(models.TransientModel):
    _name = 'strategy.skill.sync'
    _description = 'Sync Strategy Skills (Import/Export)'

    direction = fields.Selection([
        ('import', 'Import Skills'),
        ('export', 'Export Skills'),
    ], string='Direction', default='export', required=True)

    format = fields.Selection([
        ('xml', 'Odoo Data XML'),
        ('skill_md', 'SKILL.md files'),
    ], string='Format', default='skill_md', required=True)

    skill_dir = fields.Char('Skill Directory')
    skill_ids = fields.Many2many('strategy.skill', string='Skills')

    @api.onchange('direction', 'format')
    def _onchange_set_default_dir(self):
        module_path = self._get_module_skills_path()
        if self.direction == 'export' and self.format == 'skill_md':
            self.skill_dir = module_path
        elif self.direction == 'export':
            self.skill_dir = '/tmp/strategy_skills_export'
        elif self.format == 'skill_md':
            self.skill_dir = module_path
        else:
            self.skill_dir = os.path.join(os.path.dirname(module_path), 'data')

    def _get_module_skills_path(self):
        models_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(os.path.dirname(models_dir), 'static', 'skills')

    def action_sync(self):
        self.ensure_one()
        if self.direction == 'import':
            return self._do_import()
        return self._do_export()

    def _do_import(self):
        if not self.skill_dir or not os.path.isdir(self.skill_dir):
            raise UserError(_('Directory not found: %s') % self.skill_dir)
        if self.format == 'skill_md':
            return self._import_from_skill_md()
        return self._import_from_xml()

    def _import_from_skill_md(self):
        imported = updated = 0
        errors = []
        for skill_name in sorted(os.listdir(self.skill_dir)):
            skill_path = os.path.join(self.skill_dir, skill_name, 'SKILL.md')
            if not os.path.isfile(skill_path):
                continue
            try:
                fm, body = self._parse_skill_md(skill_path)
            except Exception as e:
                errors.append('%s: %s' % (skill_name, e))
                continue
            name = fm.get('name') or skill_name
            existing = self.env['strategy.skill'].search([('name', '=', name)], limit=1)
            vals = {
                'name': name, 'description': fm.get('description', ''),
                'category': fm.get('category', 'strategy'),
                'version': fm.get('version', '1.0.0'),
                'skill_content': body,
                'is_base': fm.get('is_base', 'true').lower() == 'true',
                'is_active': fm.get('is_active', 'true').lower() == 'true',
            }
            if existing:
                existing.write(vals); updated += 1
            else:
                self.env['strategy.skill'].create(vals); imported += 1
        msg = _('Import: %d new, %d updated') % (imported, updated)
        if errors:
            msg += '\n' + _('%d errors') % len(errors)
        return self._notification(msg, 'warning' if errors else 'success')

    def _import_from_xml(self):
        xml_file = os.path.join(self.skill_dir, 'strategy_skill.xml')
        if not os.path.isfile(xml_file):
            raise UserError(_('File not found: %s') % xml_file)
        import xml.etree.ElementTree as ET
        imported = updated = 0
        for rec in ET.parse(xml_file).getroot().findall('record'):
            if rec.get('model') not in ('strategy.skill', 'marketing.skill'):
                continue
            vals = {'category': 'strategy'}
            for f in rec:
                t = f.get('name')
                if t == 'name': vals['name'] = (f.text or '').strip()
                elif t == 'description': vals['description'] = (f.text or '').strip()
                elif t == 'category': vals['category'] = (f.text or 'strategy').strip()
                elif t == 'version': vals['version'] = (f.text or '1.0.0').strip()
                elif t == 'skill_content': vals['skill_content'] = (f.text or '').strip()
                elif t == 'is_base': vals['is_base'] = f.get('eval', 'False') == 'True'
                elif t == 'is_active': vals['is_active'] = f.get('eval', 'False') == 'True'
            if not vals.get('name'):
                continue
            existing = self.env['strategy.skill'].search([('name', '=', vals['name'])], limit=1)
            if existing:
                existing.write(vals); updated += 1
            else:
                self.env['strategy.skill'].create(vals); imported += 1
        return self._notification(_('XML import: %d new, %d updated') % (imported, updated), 'success')

    def _do_export(self):
        if self.format == 'xml':
            return self._export_to_xml()
        return self._export_to_skill_md()

    def _export_to_xml(self):
        output_dir = self.skill_dir or '/tmp/strategy_skills_export'
        os.makedirs(output_dir, exist_ok=True)
        xml_parts = ['<?xml version="1.0" encoding="utf-8"?><odoo>']
        for s in self.skill_ids.sorted(lambda x: x.name):
            eid = "strategy_skill_%s" % s.name.replace('-', '_').replace(' ', '_')
            xml_parts.append('  <record id="%s" model="strategy.skill">' % eid)
            xml_parts.append('    <field name="name">%s</field>' % saxutils.escape(s.name))
            xml_parts.append('    <field name="description">%s</field>' % saxutils.escape(s.description or ''))
            xml_parts.append('    <field name="category">%s</field>' % saxutils.escape(s.category or 'strategy'))
            xml_parts.append('    <field name="version">%s</field>' % saxutils.escape(s.version or '1.0.0'))
            xml_parts.append('    <field name="is_base" eval="%s"/>' % ('True' if s.is_base else 'False'))
            xml_parts.append('    <field name="is_active" eval="%s"/>' % ('True' if s.is_active else 'False'))
            xml_parts.append('    <field name="skill_content"><![CDATA[%s]]></field>' % (s.skill_content or ''))
            xml_parts.append('  </record>')
        xml_parts.append('</odoo>')
        path = os.path.join(output_dir, 'strategy_skill.xml')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_parts))
        return self._notification(_('%d exported to %s') % (len(self.skill_ids), path), 'success')

    def _export_to_skill_md(self):
        output_dir = self.skill_dir
        os.makedirs(output_dir, exist_ok=True)
        skills = self.skill_ids or self.env['strategy.skill'].search([])
        if not skills:
            raise UserError(_('No skills to export.'))
        for s in skills:
            safe = s.name.replace(' ', '-').lower()
            d = os.path.join(output_dir, safe)
            os.makedirs(d, exist_ok=True)
            md = ['---']
            md.append('name: %s' % s.name)
            md.append('description: "%s"' % (s.description or ''))
            md.append('category: %s' % (s.category or 'strategy'))
            md.append('version: %s' % (s.version or '1.0.0'))
            md.append('is_base: %s' % str(s.is_base).lower())
            md.append('is_active: %s' % str(s.is_active).lower())
            md.append('---')
            md.append(s.skill_content or '')
            with open(os.path.join(d, 'SKILL.md'), 'w', encoding='utf-8') as f:
                f.write('\n'.join(md))
        return self._notification(_('%d skills written to %s') % (len(skills), output_dir), 'success')

    @staticmethod
    def _parse_skill_md(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm = {}
                for line in parts[1].strip().split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        fm[k.strip()] = v.strip().strip('"\'')
                return fm, parts[2].strip()
        return {}, content.strip()

    @staticmethod
    def _notification(msg, t='success'):
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': _('Skill Sync'), 'message': msg, 'type': t, 'sticky': t == 'warning'}}
