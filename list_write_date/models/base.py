from lxml import etree

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "list" and "write_date" in self._fields:
            arch = etree.fromstring(result["arch"])
            if arch.tag == "list" and not arch.xpath("field[@name='write_date']"):
                node = etree.SubElement(arch, "field")
                node.set("name", "write_date")
                node.set("optional", "hide")
                result["arch"] = etree.tostring(arch, encoding="unicode")
        return result
