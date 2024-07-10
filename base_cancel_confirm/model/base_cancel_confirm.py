# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import inspect

from lxml import etree

from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.misc import frozendict


class BaseCancelConfirm(models.AbstractModel):
    _name = "base.cancel.confirm"
    _description = "Cancel Confirmation"

    _has_cancel_reason = "no"  # ["no", "optional", "required"]
    _cancel_reason_xpath = "/form/sheet/group[last()]"

    cancel_confirm = fields.Boolean(
        string="Cancel Confirmed",
        default=lambda self: self._cancel_confirm_disabled(),
        copy=False,
        help="A flag signify that this document is confirmed for cancellation",
    )
    cancel_reason = fields.Text(
        copy=False,
        help="An optional cancel reason",
    )

    def _cancel_confirm_disabled(self):
        key = "%s.cancel_confirm_disable" % self._name
        res = self.env["ir.config_parameter"].sudo().get_param(key)
        if not res:
            return True
        if res not in ("True", "False"):
            raise ValidationError(
                _("Configuration Error (%s), should be 'True' or 'False'") % key
            )
        return tools.str2bool(res)

    def open_cancel_confirm_wizard(self):
        xmlid = "base_cancel_confirm.action_cancel_confirm_wizard"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["context"] = {
            "cancel_res_model": self._name,
            "cancel_res_ids": self.ids,
            "cancel_method": inspect.stack()[1][3],
            "default_has_cancel_reason": self._has_cancel_reason,
        }
        return action

    def clear_cancel_confirm_data(self):
        self.write({"cancel_confirm": False, "cancel_reason": False})

    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "form":
            View = self.env["ir.ui.view"]
            if view_id and res.get("base_model", self._name) != self._name:
                View = View.with_context(base_model_name=res["base_model"])
            doc = etree.XML(res["arch"])
            all_models = res["models"].copy()
            for node in doc.xpath(self._cancel_reason_xpath):
                str_element = self.env["ir.qweb"]._render(
                    "base_cancel_confirm.cancel_reason_template"
                )
                new_node = etree.fromstring(str_element)
                new_arch, new_models = View.postprocess_and_fields(new_node, self._name)
                new_node = etree.fromstring(new_arch)
                for new_element in new_node:
                    node.addnext(new_element)
                for model in new_models:
                    if model in all_models:
                        continue
                    all_models[model] = new_models[model]
            res["arch"] = etree.tostring(doc)
            res["models"] = frozendict(all_models)
        return res
