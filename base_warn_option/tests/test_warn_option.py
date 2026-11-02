# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestWarnOption(TransactionCase):
    def test_search_filters(self):
        WarnOption = self.env["warn.option"]
        options = {
            warning_type: WarnOption.create(
                {
                    "name": f"Message {warning_type}",
                    "allowed_warning_type": warning_type,
                }
            )
            for warning_type in ("warning", "block", False)
        }
        arch = WarnOption.get_views([(False, "search")])["views"]["search"]["arch"]
        filters = {
            node.get("name"): safe_eval(node.get("domain"))
            for node in etree.fromstring(arch).iter("filter")
            if node.get("domain")
        }
        for filter_name, warning_type in (
            ("flt_warning_type_all", False),
            ("flt_warning_type_alert", "warning"),
            ("flt_warning_type_block", "block"),
        ):
            found = WarnOption.search(filters[filter_name]) & WarnOption.browse(
                [option.id for option in options.values()]
            )
            self.assertEqual(found, options[warning_type], filter_name)
