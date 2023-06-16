from odoo.tests.common import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class Test(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.filters_group_obj = cls.env["ir.filters.group"]
        cls.filters_obj = cls.env["ir.filters"]
        filters_group = Form(cls.filters_obj)
        filters_group.name = "Test No groupby group"
        filters_group.type = "groupby"
        filters_group.model_id = "ir.filters.group"
        filters_group.groupby_field = cls.env.ref(
            "base_custom_filter.field_ir_filters_group__name"
        )
        filters_group = filters_group.save()

        filters_group = Form(cls.filters_obj)
        filters_group.name = "Test No filters group"
        filters_group.type = "filter"
        filters_group.model_id = "ir.filters.group"
        filters_group.domain = '[["id","=",1]]'
        filters_group = filters_group.save()

    def test_get_view_content_search(self):
        with Form(self.filters_obj) as filters_search:
            filters_search.name = "Test Search Field"
            filters_search.type = "search"
            filters_search.model_id = "ir.filters.group"
            filters_search.search_field_id = self.env.ref(
                "base_custom_filter.field_ir_filters_group__display_name"
            )
            filters_search.filter_domain = "['display_name', 'ilike', self]"
            filters_search.group_ids.add(self.env.ref("base.group_system"))

        filter_search = self.filters_obj.search([("name", "=", "Test Search Field")])
        self.assertEqual(filter_search.name, "Test Search Field")

        # Test get_view() content
        view_dict = self.filters_group_obj.get_view(view_type="search")
        view_content = view_dict.get("arch", b"").decode("utf-8")
        search_string = "<field name=\"display_name\" filter_domain=\"['display_name', 'ilike', self]\"/>"  # noqa: B950
        self.assertIn(
            search_string, view_content, "The string is not in the returned view"
        )

    def test_get_view_content_filter(self):
        with Form(self.filters_group_obj) as filters_group:
            filters_group.name = "Test filters group"
            filters_group.type = "filter"
            filters_group.model_id = "ir.filters.group"
            with filters_group.filter_ids.new() as line:
                line.name = "Test filter line"
                line.domain = '[["id","=",1]]'

        filter_group = self.filters_group_obj.search(
            [("name", "=", "Test filters group")]
        )
        self.assertEqual(filter_group.name, "Test filters group")

        view_dict = self.filters_group_obj.get_view(view_type="search")
        view_content = view_dict.get("arch", b"").decode("utf-8")
        filter_name = "ir_custom_filter_" + str(
            self.filters_obj.search([("name", "=", "Test filter line")]).id
        )
        filter_string = '<filter name="{}" string="Test filter line" domain="[[&quot;id&quot;,&quot;=&quot;,1]]"/>'.format(  # noqa: B950
            filter_name
        )
        self.assertIn(
            filter_string,
            view_content,
            "The string is not in the returned view",
        )

    def test_get_view_content_groupby(self):
        with Form(self.filters_group_obj) as filters_group:
            filters_group.name = "Test groupby group"
            filters_group.type = "groupby"
            filters_group.model_id = "ir.filters.group"
            with filters_group.filter_ids.new() as line:
                line.name = "Test groupby line"
                line.groupby_field = self.env.ref(
                    "base_custom_filter.field_ir_filters_group__name"
                )

        filter_group = self.filters_group_obj.search(
            [("name", "=", "Test groupby group")]
        )
        self.assertEqual(filter_group.name, "Test groupby group")

        view_dict = self.filters_group_obj.get_view(view_type="search")
        view_content = view_dict.get("arch", b"").decode("utf-8")
        filter_name = "ir_custom_filter_" + str(
            self.filters_obj.search([("name", "=", "Test groupby line")]).id
        )
        groupby_string = '<filter name="{}" string="Test groupby line" context="{{\'group_by\': \'name\'}}"/>'.format(  # noqa: B950
            filter_name
        )
        self.assertIn(
            groupby_string,
            view_content,
            "The string is not in the returned view",
        )
