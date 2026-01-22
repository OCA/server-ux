# Copyright 2017 LasLabs Inc.
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


# This is mostly copied from base_multi_company/models/multi_company_abstract.py
# Rationale: https://github.com/OCA/server-ux/pull/1227#issuecomment-3782988133
# TODO Remove this class and, instead, inherit from base_multi_company when migrating
class DateRange(models.Model):
    _inherit = "date.range"

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        compute="_compute_company_id",
        search="_search_company_id",
        inverse="_inverse_company_id",
    )
    company_ids = fields.Many2many(
        string="Companies",
        comodel_name="res.company",
    )

    @api.depends("company_ids")
    @api.depends_context("company", "_check_company_source_id")
    def _compute_company_id(self):
        for record in self:
            # Set this priority computing the company (if included in the allowed ones)
            # for avoiding multi company incompatibility errors:
            # - If this call is done from method _check_company, the company of the
            #   record to be compared.
            # - Otherwise, current company of the user.
            company_id = (
                self.env.context.get("_check_company_source_id")
                or self.env.context.get("force_company")
                or self.env.company.id
            )
            if company_id in record.company_ids.ids:
                record.company_id = company_id
            else:
                record.company_id = record.company_ids[:1].id

    def _inverse_company_id(self):
        # To allow modifying allowed companies by non-aware base_multi_company
        # through company_id field we:
        # - Remove all companies, then add the provided one
        for record in self:
            record.company_ids = [(6, 0, record.company_id.ids)]

    def _search_company_id(self, operator, value):
        domain = [("company_ids", operator, value)]
        new_op = {"in": "=", "not in": "!="}.get(operator)
        if new_op and (False in value or None in value):
            # We need to workaround an ORM issue to find records with no company
            domain = ["|", ("company_ids", new_op, False)] + domain
        return domain

    def _multicompany_patch_vals(self, vals):
        """Patch vals to remove company_id and company_ids duplicity."""
        if "company_ids" in vals and "company_id" in vals:
            company_id = vals.pop("company_id")
            if company_id:
                vals["company_ids"].append(fields.Command.link(company_id))
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """Discard changes in company_id field if company_ids has been given."""
        for vals in vals_list:
            self._multicompany_patch_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        """Discard changes in company_id field if company_ids has been given."""
        self._multicompany_patch_vals(vals)
        return super().write(vals)
