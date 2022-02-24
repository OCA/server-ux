from odoo.tests.common import Form, SavepointCase, tagged


@tagged("post_install", "-at_install")
class Test(SavepointCase):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()
        filters_obj = cls.env["ir.filters"]
        filters_group = Form(filters_obj)
        filters_group.name = "Test No groupby group"
        filters_group.type = "groupby"
        filters_group.model_id = "ir.filters.group"
        filters_group.groupby_field = cls.env.ref(
            "base_custom_filter.field_ir_filters_group__name"
        )
        filters_group = filters_group.save()

        filters_group = Form(filters_obj)
        filters_group.name = "Test No filters group"
        filters_group.type = "filter"
        filters_group.model_id = "ir.filters.group"
        filters_group.domain = '[["id","=",1]]'
        filters_group = filters_group.save()

    def test_sale_order_line(self):
        filters_group_obj = self.env["ir.filters.group"]
        filters_obj = self.env["ir.filters"]
        filters_obj.unlink()
        filters_group_obj.unlink()
        with Form(filters_group_obj) as filters_group:
            filters_group.name = "Test filters group"
            filters_group.type = "filter"
            filters_group.model_id = "ir.filters.group"
            with filters_group.filter_ids.new() as line:
                line.name = "Test filter line"
                line.domain = '[["id","=",1]]'

        filter_group = filters_group_obj.search([("name", "=", "Test filters group")])
        self.assertEqual(filter_group.name, "Test filters group")

        with Form(filters_group_obj) as filters_group:
            filters_group.name = "Test groupby group"
            filters_group.type = "groupby"
            filters_group.model_id = "ir.filters.group"
            with filters_group.filter_ids.new() as line:
                line.name = "Test groupby line"
                line.groupby_field = self.env.ref(
                    "base_custom_filter.field_ir_filters_group__name"
                )

        filters_group_obj.fields_view_get(view_type="search")
        filter_group.unlink()
