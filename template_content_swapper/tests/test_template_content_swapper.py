# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestTemplateStringSwapper(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.view_obj = cls.env["ir.ui.view"]
        cls.main_company = cls.env.company
        cls.report = cls.env.ref("web.action_report_externalpreview")
        cls.template = cls.report.report_name
        ja = (
            cls.env["res.lang"]
            .with_context(active_test=False)
            .search([("code", "=", "ja_JP")])
        )
        cls.env["base.language.install"].create({"lang_ids": ja.ids}).lang_install()

    def _render_report_html(self, company=None, lang=None):
        company = company or self.env.company
        view_obj = self.view_obj
        if company:
            view_obj = view_obj.with_company(company)
        if lang:
            view_obj = view_obj.with_context(lang=lang)
        view = view_obj._get(self.template).sudo()
        values = {"company": company, "report_type": "pdf", "o": view}
        return view_obj._render_template(self.template, values)

    def _create_mapping(self, content_from, content_to, lang, domain=None):
        vals = {
            "report_id": self.report.id,
            "content_from": content_from,
            "content_to": content_to,
            "lang": lang,
        }
        if domain:
            vals["domain"] = domain
        return self.env["template.content.mapping"].create(vals)

    def test_template_string_swapper(self):
        result = self._render_report_html(lang="en_US")
        self.assertTrue("Page" in str(result))
        self._create_mapping(
            content_from="Page",
            content_to="Slide",
            lang="en_US",
        )
        result = self._render_report_html(lang="en_US")
        self.assertFalse("Page" in str(result))
        self.assertTrue("Slide" in str(result))
        # JA
        result = self._render_report_html(lang="ja_JP")
        self.assertTrue("ページ" in str(result))
        self._create_mapping(
            content_from="ページ",
            content_to="スライド",
            lang="ja_JP",
        )
        result = self._render_report_html(lang="ja_JP")
        self.assertFalse("ページ" in str(result))
        self.assertTrue("スライド" in str(result))

    def test_template_string_swapper_with_domain(self):
        test_company = self.env["res.company"].create({"name": "Test Company"})
        domain = f"[('id', '=', {test_company.id})]"
        # EN for test_company
        result = self._render_report_html(company=test_company, lang="en_US")
        self.assertTrue("Page" in str(result))
        self._create_mapping(
            domain=domain,
            content_from="Page",
            content_to="Slide",
            lang="en_US",
        )
        result = self._render_report_html(company=test_company, lang="en_US")
        self.assertFalse("Page" in str(result))
        self.assertTrue("Slide" in str(result))
        # Ensure it doesn't apply to main company
        result = self._render_report_html(company=self.main_company, lang="en_US")
        self.assertFalse("Slide" in str(result))
        # JA for test_company
        result = self._render_report_html(company=test_company, lang="ja_JP")
        self.assertTrue("ページ" in str(result))
        self._create_mapping(
            domain=domain,
            content_from="ページ",
            content_to="スライド",
            lang="ja_JP",
        )
        result = self._render_report_html(company=test_company, lang="ja_JP")
        self.assertTrue("スライド" in str(result))
        # Ensure it doesn't apply to main company (JA)
        result = self._render_report_html(company=self.main_company, lang="ja_JP")
        self.assertFalse("スライド" in str(result))
