# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

from markupsafe import Markup

from odoo import api, models
from odoo.osv.expression import normalize_domain
from odoo.tools.profiler import QwebTracker
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

DIV_TAG_RE = re.compile(r"<(/?)div\b([^>]*)>")
ARTICLE_CLASS_RE = re.compile(r'(?:^|\s)class="[^"]*article[^"]*"')
OE_ID_RE = re.compile(r'\sdata-oe-id="(\d+)"')


class IrQWeb(models.AbstractModel):
    _inherit = "ir.qweb"

    def _apply_mappings(self, html_str, mappings, res_id=None, match_map=None):
        """Apply mappings to HTML string; with match_map, only those matching res_id."""
        for m in mappings:
            if match_map is not None and res_id not in match_map.get(m.id, set()):
                continue
            html_str = html_str.replace(m.content_from, m.content_to or "")
        return html_str

    def _get_match_map(self, domain_mappings, res_ids):
        """Return {mapping_id: set of IDs among res_ids matching the mapping domain}."""
        result = {}
        eval_ctx = self.env["template.content.mapping"]._get_eval_context()
        for m in domain_mappings:
            if not m.report_model:
                continue
            records = self.env[m.report_model].browse(res_ids)
            try:
                dom = normalize_domain(safe_eval(m.domain, eval_ctx))
                # browse() keeps archived records, unlike search()
                result[m.id] = set(records.filtered_domain(dom).ids)
            except Exception:
                _logger.warning(
                    "Invalid domain on template.content.mapping %s: %s",
                    m.id,
                    m.domain,
                )
        return result

    def _get_article_spans(self, html_str):
        """Return [(start, end, res_id)] of the report article divs in html_str."""
        spans = []
        start = res_id = None
        depth = 0
        for tag in DIV_TAG_RE.finditer(html_str):
            closing, attrs = tag.groups()
            if start is None:
                oe_id = OE_ID_RE.search(attrs)
                if (
                    not closing
                    and oe_id
                    and ARTICLE_CLASS_RE.search(attrs)
                    and re.search(r"\sdata-oe-model=", attrs)
                ):
                    start, res_id, depth = tag.start(), int(oe_id.group(1)), 1
                continue
            depth += -1 if closing else 1
            if not depth:
                spans.append((start, tag.end(), res_id))
                start = None
        return spans

    def _apply_article_mappings(self, html_str, spans, domain_mappings, match_map):
        """Apply domain mappings to each article span of a multi-record render."""
        # Slicing the raw string keeps the markup content_from was written against
        parts = []
        pos = 0
        for start, end, res_id in spans:
            parts.append(html_str[pos:start])
            parts.append(
                self._apply_mappings(
                    html_str[start:end], domain_mappings, res_id, match_map
                )
            )
            pos = end
        parts.append(html_str[pos:])
        return "".join(parts)

    def _apply_domain_mappings(self, html_str, domain_mappings):
        """Apply domain mappings to the report articles whose record matches."""
        if not domain_mappings:
            return html_str
        spans = self._get_article_spans(html_str)
        if not spans:
            return html_str
        match_map = self._get_match_map(domain_mappings, [span[2] for span in spans])
        if len(spans) == 1:
            # Single record → domain mappings can be applied globally
            return self._apply_mappings(
                html_str, domain_mappings, spans[0][2], match_map
            )
        return self._apply_article_mappings(html_str, spans, domain_mappings, match_map)

    @QwebTracker.wrap_render
    @api.model
    def _render(self, template, values=None, **options):
        result = super()._render(template, values=values, **options)
        values = values or {}
        if not isinstance(template, str):
            return result
        result_str = str(result)
        request = values.get("request")
        if request:
            # For views
            lang_code = request.env.lang
        else:
            # For reports
            lang_match = re.search(r'data-oe-lang="([^"]+)"', result_str)
            lang_code = lang_match.group(1) if lang_match else "en_US"
        view = self.env["ir.ui.view"]._get(template)
        mappings = (
            self.env["template.content.mapping"]
            .sudo()
            .search([("template_id", "=", view.id), ("lang", "in", [lang_code, False])])
        )
        if not mappings:
            return result
        domain_mappings = [m for m in mappings if m._has_domain()]
        global_mappings = [m for m in mappings if not m._has_domain()]
        # Domain mappings first, so a record-specific mapping wins over a global one
        result_str = self._apply_domain_mappings(result_str, domain_mappings)
        return Markup(self._apply_mappings(result_str, global_mappings))
