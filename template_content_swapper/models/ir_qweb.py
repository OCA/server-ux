# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from markupsafe import Markup

from odoo import api, models
from odoo.tools.profiler import QwebTracker


class IrQWeb(models.AbstractModel):
    _inherit = "ir.qweb"

    @QwebTracker.wrap_render
    @api.model
    def _render(self, template, values=None, **options):
        result = super()._render(template, values=values, **options)
        values = values or {}
        if not isinstance(template, str):
            return result
        result_str = str(result)
        lang_code = "en_US"
        request = values.get("request")
        if request:
            # For views
            lang_code = request.env.lang
        else:
            # For reports
            lang_match = re.search(r'data-oe-lang="([^"]+)"', result_str)
            if lang_match:
                lang_code = lang_match.group(1)
        view = self.env["ir.ui.view"]._get(template)
        content_mappings = (
            self.env["template.content.mapping"]
            .sudo()
            .search(
                [
                    ("template_id", "=", view.id),
                    "|",
                    ("lang", "=", lang_code),
                    ("lang", "=", False),
                ]
            )
        )
        if content_mappings:
            for mapping in content_mappings:
                content_from = mapping.content_from
                content_to = mapping.content_to or ""
                result_str = result_str.replace(content_from, content_to)
            result = Markup(result_str)
        return result
