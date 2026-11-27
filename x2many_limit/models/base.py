from lxml import etree

from odoo import api, models

PARAM = "x2many_limit.limit"


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        # done after the view cache: a new value applies at once
        limit = self.env["ir.config_parameter"].sudo().get_int(PARAM)
        if limit > 0 and "<field" in result["arch"]:
            arch = etree.fromstring(result["arch"])
            # the web client shows 40 lines in a x2many list without a limit
            nodes = arch.xpath(
                "//field/list[not(@limit)] | //field/kanban[not(@limit)]"
            )
            for node in nodes:
                node.set("limit", str(limit))
            if nodes:
                result["arch"] = etree.tostring(arch, encoding="unicode")
        return result
