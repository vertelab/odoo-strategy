# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# IMPORTANT: Import order matters for field resolution.
# Models that define the Many2one side (plan_id) must be imported BEFORE
# models that reference them via One2many.
from . import business_model_canvas
from . import swot_analysis
from . import value_proposition_canvas
from . import okr
from . import strategy_risk
from . import strategy_action
from . import strategy_plan  # depends on plan_id in all above models
from . import strategy_skill
from . import strategy_skill_import
