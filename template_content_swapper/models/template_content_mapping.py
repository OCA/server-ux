# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.osv.expression import normalize_domain
from odoo.tools.safe_eval import safe_eval


class TemplateContentMapping(models.Model):
    _name = "template.content.mapping"
    _description = "Template Content Mapping"
    _order = "template_id, content_from"

    @api.model
    def _lang_get(self):
        return self.env["res.lang"].get_installed()

    name = fields.Char(compute="_compute_name", store=True, readonly=True)
    report_id = fields.Many2one("ir.actions.report")
    report_model = fields.Char(compute="_compute_report_model", store=True)
    template_id = fields.Many2one(
        "ir.ui.view",
        domain=[("type", "=", "qweb")],
        required=True,
        compute="_compute_template_id",
        store=True,
        readonly=False,
        precompute=True,
        help="Select the main template of the report / frontend page to be modified.",
    )
    domain = fields.Char(
        help="Optional domain on the report records. The mapping is applied "
        "only if the record in the report matches this domain. "
        "Example: [('partner_id', '=', 1)]",
    )
    lang = fields.Selection(
        _lang_get,
        string="Language",
        default=lambda self: self.env.lang,
        help="If no language is selected, the mapping will be applied to all "
        "languages.",
    )
    content_from = fields.Char(
        required=True,
        help="Set the content (string) to be replaced. e.g. 'Salesperson'.",
    )
    content_to = fields.Char(
        help="Set your new content (string). e.g. 'Sales Representative'.",
    )

    @api.depends("report_id", "template_id")
    def _compute_report_model(self):
        for rec in self:
            if rec.report_id:
                rec.report_model = rec.report_id.model
            else:
                report = self.env["ir.actions.report"].search(
                    [("report_name", "=", rec.template_id.key)], limit=1
                )
                rec.report_model = report.model if report else False

    @api.depends("content_from", "content_to")
    def _compute_name(self):
        for record in self:
            record.name = False
            if record.content_from:
                record.name = f"{record.content_from} -> {record.content_to or ''}"

    @api.depends("report_id")
    def _compute_template_id(self):
        for rec in self:
            rec.template_id = False
            if rec.report_id:
                report_name = rec.report_id.report_name
                rec.template_id = self.env["ir.ui.view"]._get(report_name).sudo()

    def _get_eval_context(self):
        return {
            "time": tools.safe_eval.time,
            "datetime": tools.safe_eval.datetime,
            "dateutil": tools.safe_eval.dateutil,
            "timezone": tools.safe_eval.pytz.timezone,
            "context_today": lambda: fields.Date.context_today(self),
        }

    @api.constrains("domain", "template_id")
    def _check_domain_format(self):
        for rec in self:
            if not rec.domain:
                continue
            if not self.env["ir.actions.report"].search(
                [("report_name", "=", rec.template_id.key)], limit=1
            ):
                raise ValidationError(
                    _(
                        "A domain can only be set for report templates. "
                        "The template '%(template)s' is not linked to any report."
                    )
                    % {"template": rec.template_id.name}
                )
            try:
                normalize_domain(safe_eval(rec.domain, rec._get_eval_context()))
            except Exception as e:
                raise ValidationError(
                    _("Invalid domain format: %(domain)s.\nError: %(error)s")
                    % {"domain": rec.domain, "error": e}
                ) from e

    def open_template_mapping(self):
        multi_lang = len(self.env["res.lang"].get_installed()) > 1
        return {
            "type": "ir.actions.act_window",
            "name": "Template Content Mappings",
            "res_model": "template.content.mapping",
            "view_mode": "list",
            "context": {"multi_lang": multi_lang},
        }
