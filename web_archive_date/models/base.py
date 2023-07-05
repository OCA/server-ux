# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models

from odoo.addons.base_archive_date.models.base import LOG_ARCHIVE_DATE, LOG_ARCHIVE_UID


class Base(models.AbstractModel):
    _inherit = "base"

    def get_metadata(self):
        def merge_lists_of_dicts(original, new, key):
            merged_dict = {}
            for item in original:
                merged_dict[item[key]] = item
            for item in new:
                merged_dict.setdefault(item[key], {}).update(item)
            merged_list = list(merged_dict.values())
            return merged_list

        result = super(Base, self).get_metadata()
        fields_list = list(self._fields)
        if LOG_ARCHIVE_DATE in fields_list and LOG_ARCHIVE_UID in fields_list:
            archive_dict = self.read([LOG_ARCHIVE_DATE, LOG_ARCHIVE_UID])
            return merge_lists_of_dicts(result, archive_dict, "id")
        return result
