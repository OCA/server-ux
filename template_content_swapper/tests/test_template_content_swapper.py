# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
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
        self.assertTrue("Page:" in str(result))
        self._create_mapping(
            content_from="Page:",
            content_to="Page No.:",
            lang="en_US",
        )
        result = self._render_report_html(lang="en_US")
        self.assertFalse("Page:" in str(result))
        self.assertTrue("Page No.:" in str(result))
        # JA
        result = self._render_report_html(lang="ja_JP")
        self.assertTrue("ページ:" in str(result))
        self._create_mapping(
            content_from="ページ:",
            content_to="ページ番号:",
            lang="ja_JP",
        )
        result = self._render_report_html(lang="ja_JP")
        self.assertFalse("ページ:" in str(result))
        self.assertTrue("ページ番号:" in str(result))

    def test_template_string_swapper_with_domain(self):
        test_company = self.env["res.company"].create({"name": "Test Company"})
        domain = f"[('id', '=', {test_company.id})]"
        # EN for test_company
        result = self._render_report_html(company=test_company, lang="en_US")
        self.assertTrue("Page:" in str(result))
        self._create_mapping(
            domain=domain,
            content_from="Page:",
            content_to="Page No.:",
            lang="en_US",
        )
        result = self._render_report_html(company=test_company, lang="en_US")
        self.assertFalse("Page:" in str(result))
        self.assertTrue("Page No.:" in str(result))
        # Ensure it doesn't apply to main company
        result = self._render_report_html(company=self.main_company, lang="en_US")
        self.assertFalse("Page No.:" in str(result))
        # JA for test_company
        result = self._render_report_html(company=test_company, lang="ja_JP")
        self.assertTrue("ページ:" in str(result))
        self._create_mapping(
            domain=domain,
            content_from="ページ:",
            content_to="ページ番号:",
            lang="ja_JP",
        )
        result = self._render_report_html(company=test_company, lang="ja_JP")
        self.assertTrue("ページ番号:" in str(result))
        # Ensure it doesn't apply to main company (JA)
        result = self._render_report_html(company=self.main_company, lang="ja_JP")
        self.assertFalse("ページ番号:" in str(result))

    def _create_qweb_view(self, key, arch):
        return self.env["ir.ui.view"].create(
            {"name": key, "key": key, "type": "qweb", "arch": arch}
        )

    def _create_partner_report(self):
        view = self._create_qweb_view(
            "template_content_swapper.test_multi",
            """<t t-name="template_content_swapper.test_multi">
                <div class="header">Report Title</div>
                <t t-foreach="docs" t-as="o">
                    <div class="article" t-att-data-oe-model="o._name"
                        t-att-data-oe-id="o.id">
                        <p>Name:<br/><span t-out="o.name"/></p>
                    </div>
                </t>
            </t>""",
        )
        return self.env["ir.actions.report"].create(
            {
                "name": "Test Multi",
                "model": "res.partner",
                "report_type": "qweb-html",
                "report_name": view.key,
            }
        )

    def _create_report_mapping(self, report, content_from, content_to, domain=False):
        return self.env["template.content.mapping"].create(
            {
                "report_id": report.id,
                "domain": domain,
                "content_from": content_from,
                "content_to": content_to,
                "lang": False,
            }
        )

    def _render_partners(self, report, partners):
        return (
            self.env["ir.actions.report"]
            ._render_qweb_html(report.report_name, partners.ids)[0]
            .decode()
        )

    def _create_partners(self):
        return self.env["res.partner"].create(
            [{"name": "Partner A"}, {"name": "Partner B"}]
        )

    def test_domain_mapping_multi_record_keeps_markup(self):
        # Fails if articles are re-serialized (e.g. <br/> -> <br>) before matching
        report = self._create_partner_report()
        partner_a, partner_b = self._create_partners()
        self._create_report_mapping(
            report, "Name:<br/>", "Customer:<br/>", f"[('id', '=', {partner_a.id})]"
        )
        result = self._render_partners(report, partner_a | partner_b)
        self.assertIn("Customer:<br/><span>Partner A</span>", result)
        self.assertIn("Name:<br/><span>Partner B</span>", result)

    def test_domain_mapping_wins_over_global_mapping(self):
        # Fails if global mappings run first and consume the shared content_from
        report = self._create_partner_report()
        partner_a, partner_b = self._create_partners()
        self._create_report_mapping(report, "Name:", "Label:")
        self._create_report_mapping(
            report, "Name:", "Customer:", f"[('id', '=', {partner_a.id})]"
        )
        result = self._render_partners(report, partner_a | partner_b)
        self.assertIn("Customer:<br/><span>Partner A</span>", result)
        self.assertIn("Label:<br/><span>Partner B</span>", result)

    def test_empty_domain_mapping_applies_outside_articles(self):
        # Fails if '[]' is treated as a domain, limiting it to the article blocks
        report = self._create_partner_report()
        self._create_report_mapping(report, "Report Title", "Partner List", "[]")
        result = self._render_partners(report, self._create_partners())
        self.assertIn("Partner List", result)
        self.assertNotIn("Report Title", result)

    def test_domain_constraint(self):
        report = self._create_partner_report()
        with self.assertRaises(ValidationError):
            self._create_report_mapping(
                report, "Name:", "X", "[('no_such_field', '=', 1)]"
            )
        view = self._create_qweb_view(
            "template_content_swapper.test_no_report",
            '<t t-name="template_content_swapper.test_no_report"><p>Name:</p></t>',
        )
        with self.assertRaises(ValidationError):
            self.env["template.content.mapping"].create(
                {
                    "template_id": view.id,
                    "domain": "[('id', '=', 1)]",
                    "content_from": "Name:",
                }
            )
