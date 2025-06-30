from lxml import etree

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    _search_today_create_fields = "create_date"
    _search_today_update_fields = "write_date"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        # Inherit the get_view method to inject the 'Today' filter
        # Inject 'Today' filter in search views.
        res = super().get_view(view_id, view_type, **options)
        if view_type != "search" or (
            (
                not self._search_today_create_fields
                or self._search_today_create_fields not in self._fields
            )
            and (
                not self._search_today_update_fields
                or self._search_today_update_fields not in self._fields
            )
        ):
            return res
        arch = etree.fromstring(res["arch"])

        def _add_filter_date(filtern_name, filter_string, domain):
            """Helper function to add a date filter."""
            today_filter = etree.Element(
                "filter",
                {
                    "name": filtern_name,
                    "string": filter_string,
                    "domain": domain,
                },
            )
            # Add the 'Today' filter to the search view
            arch.append(today_filter)

        domain = (
            "[('{date_field}', '>', "
            "(context_today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))]"
        )
        if self._search_today_create_fields:
            # Define the 'Today' filter
            _add_filter_date(
                filtern_name="auto_created_today",
                filter_string="Created Today",
                domain=domain.format(
                    date_field=self._search_today_create_fields,
                ),
            )

        if self._search_today_update_fields:
            # Define the 'Today' filter for updates
            _add_filter_date(
                filtern_name="auto_updated_today",
                filter_string="Updated Today",
                domain=domain.format(
                    date_field=self._search_today_update_fields,
                ),
            )
        res["arch"] = etree.tostring(arch, encoding="unicode")
        return res
