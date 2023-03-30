# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


import logging

from openupgradelib.openupgrade_merge_records import merge_records

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger("server_action_merge")


class ServerActionMergeWizard(models.TransientModel):
    _name = "server.action.merge.wizard"
    _description = "Merge records"

    action_id = fields.Many2one("ir.actions.server", required=True, ondelete="cascade")
    model_id = fields.Many2one(
        "ir.model",
        default=lambda self: self.env["ir.model"].search(
            [("model", "=", self.env.context.get("active_model"))]
        ),
        ondelte="cascade",
    )
    target_line_id = fields.Many2one("server.action.merge.wizard.line", string="Target")
    target_line_xmlid = fields.Char(related="target_line_id.xmlid")
    line_ids = fields.One2many(
        "server.action.merge.wizard.line",
        "wizard_id",
        string="Merge records",
        required=True,
        default=lambda self: self._default_line_ids(),
    )
    xmlid_count = fields.Integer(compute="_compute_xmlid_count")

    def action_merge(self):
        """Merge records in line_ids into the one selected in target_line_id"""
        self.ensure_one()
        if self.action_id.groups_id and not (
            self.action_id.groups_id & self.env.user.groups_id
        ):
            raise exceptions.AccessError(
                _("You don't have enough access rights to run this action.")
            )

        records = self.line_ids.mapped("record") - self.target_line_id.record
        self._merge_records(self.target_line_id.record, records)

        return {
            "type": "ir.actions.act_window",
            "name": _("Merge result"),
            "res_model": self.target_line_id.record._name,
            "res_id": self.target_line_id.record.id,
            "view_mode": "form",
        }

    def _merge_records(self, target, records, delete=True):
        """Merge records, possibly merging records the model inherits from"""
        to_delete = {}
        for field_name in target._inherits.values():
            inherit_target = target[field_name]
            inherit_records = records.mapped(field_name) - inherit_target
            if inherit_target and inherit_records:
                to_delete.update(
                    **self._merge_records(inherit_target, inherit_records, False)
                )

        getattr(target, "_server_action_merge_pre", lambda *args: None)(records, self)
        # fix for quants, supplierinfo

        _logger.info("Merging %s into %s", records, self.target_line_id.record)
        merge_records(
            self.env(*(self.env.args[:3] + tuple([self.action_id.merge_sudo]))),
            records._name,
            records.ids,
            target.id,
            method=self.action_id.merge_method,
            delete=False,
            model_table=records._table,
            # TODO: allow this to be configured in the server action
            field_spec={
                name: "first_not_null"
                for name, field in target._fields.items()
                if field.type in ("char", "float")
            },
        )
        if self.action_id.merge_handling in ("delete", "deactivate"):
            to_delete.setdefault(target._name, target.browse([]))
            to_delete[target._name] += records

        if delete:
            for records in to_delete.values():
                if self.action_id.merge_handling == "deactivate":
                    records.write({"active": False})
                else:
                    records.unlink()

        getattr(target, "_server_action_merge_post", lambda *args: None)(records, self)

        return to_delete

    def _default_line_ids(self):
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids", [])
        return [
            (0, 0, {"record": "%s,%d" % (active_model, active_id)})
            for active_id in active_ids
            if active_model
        ]

    @api.depends("line_ids")
    def _compute_xmlid_count(self):
        for this in self:
            this.xmlid_count = len(this.line_ids.filtered("xmlid"))

    @api.onchange("line_ids")
    def _onchange_line_ids(self):
        record = (
            self.target_line_id
            if getattr(self.target_line_id.id, "origin", self.target_line_id.id)
            in [getattr(record.id, "origin", record.id) for record in self.line_ids]
            else self.line_ids.filtered("xmlid")[:1] or self.line_ids[:1]
        )
        self.target_line_id = getattr(record.id, "origin", record.id or False)


class ServerActionMergeWizardLine(models.TransientModel):
    _name = "server.action.merge.wizard.line"
    _description = "Merge record line"
    _rec_name = "record"

    sequence = fields.Integer("Sequence")
    record = fields.Reference(
        selection=lambda self: self.env["ir.model"]
        .search([])
        .mapped(lambda model: (model.model, model.name)),
        string="Record",
        required=True,
        readonly=True,
    )
    wizard_id = fields.Many2one(
        "server.action.merge.wizard", required=True, ondelete="cascade"
    )
    xmlid = fields.Char("XMLID", compute="_compute_xmlid")

    @api.depends("record")
    def _compute_xmlid(self):
        for this in self:
            this.xmlid = (
                self.env["ir.model.data"]
                .search(
                    [
                        ("module", "not like", "\\_\\_%\\_\\_"),
                        ("model", "=", this.record._name),
                        ("res_id", "=", this.record.id),
                    ],
                    limit=1,
                )
                .complete_name
            )
