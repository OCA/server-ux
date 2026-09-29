# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def get_views(self, views, options=None):
        """Dynamically modify form view arch to hide the toggle_active button."""
        res = super().get_views(views, options=options)

        active_name = self._active_name
        if not active_name:
            return res

        can_archive = self.env["ir.model.access"].check(
            self._name, "archive", raise_exception=False
        )
        can_unarchive = self.env["ir.model.access"].check(
            self._name, "unarchive", raise_exception=False
        )

        if can_archive and can_unarchive:
            return res

        if "views" in res:
            for view_type in ["form", "list"]:
                if view_type in res["views"]:
                    arch = res["views"][view_type].get("arch")
                    if arch:
                        doc = etree.fromstring(arch)
                        # Look for both the toggle_active button and
                        #  the active field itself
                        elements = doc.xpath(
                            "//button[@name='toggle_active']"
                        ) + doc.xpath(f"//field[@name='{active_name}']")
                        for elem in elements:
                            invisible_attr = ""
                            if not can_archive and not can_unarchive:
                                invisible_attr = "True"
                            elif can_archive and not can_unarchive:
                                # Can archive:
                                # hide if record is already archived (active=False)
                                invisible_attr = f"not {active_name}"
                            elif not can_archive and can_unarchive:
                                # Can unarchive:
                                # hide if record is already active (active=True)
                                invisible_attr = active_name

                            if invisible_attr:
                                existing = elem.get("invisible")
                                if existing:
                                    elem.set(
                                        "invisible",
                                        f"({existing}) or ({invisible_attr})",
                                    )
                                else:
                                    elem.set("invisible", invisible_attr)

                        res["views"][view_type]["arch"] = etree.tostring(
                            doc, encoding="unicode"
                        )

        return res
