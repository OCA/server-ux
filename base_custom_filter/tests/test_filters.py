from odoo.tests.common import Form, TransactionCase


class TestSaleOrderLine(TransactionCase):
    def test_sale_order_line(self):
        filters_group_obj = self.env["ir.filters.group"]
        with Form(filters_group_obj) as filters_group:
            filters_group.name = "Test filters group"
            filters_group.type = "filter"
            filters_group.model_id = "ir.filters.group"
            with filters_group.filter_ids.new() as line:
                line.name = "Test filter line"
                line.domain = '[["id","=",1]]'
        filters_group_obj.fields_view_get(view_type="tree")
        filter_group = filters_group_obj.search([("name", "=", "Test filters group")])
        self.assertEqual(filter_group.name, "Test filters group")
        with Form(filters_group_obj) as filters_group:
            filters_group.name = "Test No filters group"
            filters_group.type = "filter"
            filters_group.model_id = "ir.filters.group"
        with Form(filters_group_obj) as filters_group:
            filters_group.name = "Test groupby group"
            filters_group.type = "groupby"
            filters_group.model_id = "ir.filters.group"
            with filters_group.filter_ids.new() as line:
                line.name = "Test groupby line"
                line.groupby_field = self.env.ref(
                    "base_custom_filter.field_ir_filters_group__name"
                )
        with Form(filters_group_obj) as filters_group:
            filters_group.name = "Test No groupby group"
            filters_group.type = "groupby"
            filters_group.model_id = "ir.filters.group"
        filter_group.unlink()
