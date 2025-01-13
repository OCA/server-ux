# © 2016 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from lxml import etree

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        arch_str = etree.tostring(arch, encoding="unicode")
        # Append base_technical_features.group_technical_features
        # This adds additional access to elements that were restricted to
        # "base.group_no_one"
        arch_str = re.sub(
            r"(!?)base\.group_no_one",
            r"\1base.group_no_one,\1base_technical_features.group_technical_features",
            arch_str,
        )
        arch = etree.fromstring(arch_str)

        return arch, view
