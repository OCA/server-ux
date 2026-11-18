# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

from lxml import html
from markupsafe import Markup

from odoo import api, models
from odoo.tools.profiler import QwebTracker
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

ARTICLE_XPATH = '//div[contains(@class, "article") and @data-oe-model and @data-oe-id]'


class IrQWeb(models.AbstractModel):
    _inherit = "ir.qweb"

    def _apply_mappings(self, html_str, mappings, model_name=None, res_id=None):
        """Apply mappings to HTML string, optionally filtering by record domain."""
        for m in mappings:
            if m.domain:
                if m.report_model and m.report_model != model_name:
                    continue
                if not self._record_matches_domain(model_name, res_id, m.domain):
                    continue
            html_str = html_str.replace(m.content_from, m.content_to or "")
        return html_str

    def _record_matches_domain(self, model_name, res_id, domain_str):
        """Check if record (model_name, res_id) matches the given domain."""
        try:
            dom = safe_eval(domain_str)
        except Exception:
            _logger.warning(
                "Invalid domain on template.content.mapping for %s,%s: %s",
                model_name,
                res_id,
                domain_str,
            )
            return False
        return bool(self.env[model_name].search_count([("id", "=", res_id)] + dom))

    def _apply_mappings_on_articles(self, articles, domain_mappings):
        """Apply domain mappings per article block for multi-record renders."""
        for article in articles:
            article_html = html.tostring(article, encoding="unicode")
            new_html = self._apply_mappings(
                article_html,
                domain_mappings,
                article.get("data-oe-model"),
                int(article.get("data-oe-id")),
            )
            if new_html != article_html:
                try:
                    article.getparent().replace(article, html.fromstring(new_html))
                except Exception:
                    _logger.exception(
                        "Failed to replace article HTML for %s,%s",
                        article.get("data-oe-model"),
                        article.get("data-oe-id"),
                    )

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
        global_mappings = [m for m in mappings if not m.domain]
        domain_mappings = [m for m in mappings if m.domain]
        result_str = self._apply_mappings(result_str, global_mappings)
        if not domain_mappings:
            return Markup(result_str)
        try:
            root = html.fromstring(result_str)
        except Exception:
            _logger.warning(
                "Failed to parse HTML for template %s, skipping domain-based mappings.",
                template,
            )
            return Markup(result_str)
        articles = root.xpath(ARTICLE_XPATH)
        if not articles:
            return Markup(result_str)
        if len(articles) == 1:
            # Single record → domain mappings can be applied globally
            article = articles[0]
            result_str = self._apply_mappings(
                result_str,
                domain_mappings,
                article.get("data-oe-model"),
                int(article.get("data-oe-id")),
            )
            return Markup(result_str)
        self._apply_mappings_on_articles(articles, domain_mappings)
        final_html = html.tostring(root, encoding="unicode")
        return Markup(final_html)
