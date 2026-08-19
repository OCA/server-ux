from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase, tagged


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
        # noqa: B950
        search_string = (
            '<field name="display_name" '
            "filter_domain=\"['display_name', 'ilike', self]\"/>"
        )
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
        # noqa: B950
        filter_string = (
            f'<filter name="{filter_name}" '
            'string="Test filter line" '
            'domain="[[&quot;id&quot;,&quot;=&quot;,1]]"/>'
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
        groupby_string = (
            f'<filter name="{filter_name}" '
            'string="Test groupby line" '
            "context=\"{'group_by': 'name'}\"/>"
        )
        self.assertIn(
            groupby_string,
            view_content,
            "The string is not in the returned view",
        )

    def test_get_filters_excludes_non_favorites(self):
        """Test that get_filters excludes non-favorite filter types."""
        # Create a non-favorite filter
        self.filters_obj.create(
            {
                "name": "Non-Favorite Filter",
                "type": "filter",
                "model_id": "ir.filters.group",
                "domain": '[["id","=",1]]',
            }
        )
        # Create a favorite filter
        self.filters_obj.create(
            {
                "name": "Favorite Filter",
                "type": "favorite",
                "model_id": "ir.filters.group",
                "domain": '[["id","=",2]]',
            }
        )
        results = self.filters_obj.get_filters("ir.filters.group")
        result_names = [r["name"] for r in results]
        self.assertNotIn("Non-Favorite Filter", result_names)
        self.assertIn("Favorite Filter", result_names)

    def test_insert_xpath_validation(self):
        group = self.filters_group_obj.create(
            {
                "name": "Test Valid XPath",
                "type": "filter",
                "model_id": "ir.filters.group",
                "insert_xpath": "//filter[@name='Without_filters']",
            }
        )
        with self.assertRaises(ValidationError):
            group.write({"insert_xpath": "///invalid[xpath"})

    def test_filter_with_custom_xpath(self):
        """Test filter insertion with custom XPath and separator position."""
        with Form(self.filters_group_obj) as filters_group:
            filters_group.name = "Test XPath Group"
            filters_group.type = "filter"
            filters_group.model_id = "ir.filters.group"
            filters_group.insert_xpath = "//filter[@name='Without_filters']"
            filters_group.insert_position = "before"
            filters_group.separator_position = "after"
            with filters_group.filter_ids.new() as line:
                line.name = "XPath Filter"
                line.domain = '[["id","=",99]]'
        view_dict = self.filters_group_obj.get_view(view_type="search")
        view_content = view_dict.get("arch", b"").decode("utf-8")
        self.assertIn("XPath Filter", view_content)
        # Verify the filter is inserted before Without_filters
        filter_pos = view_content.find("XPath Filter")
        target_pos = view_content.find("Without_filters")
        self.assertLess(filter_pos, target_pos)
        # Verify separator exists after the filter (before Without_filters)
        separator_pos = view_content.find("<separator/>", filter_pos)
        self.assertLess(separator_pos, target_pos)
        # Update to no separator and verify it's removed
        group = self.filters_group_obj.search([("name", "=", "Test XPath Group")])
        group.write({"separator_position": "none"})
        view_dict = self.filters_group_obj.get_view(view_type="search")
        view_content = view_dict.get("arch", b"").decode("utf-8")
        filter_pos = view_content.find("XPath Filter")
        target_pos = view_content.find("Without_filters")
        # No separator should exist between filter and target
        between_content = view_content[filter_pos:target_pos]
        self.assertNotIn("<separator/>", between_content)

    def test_get_view_content_date_filter(self):
        with Form(self.filters_obj) as date_filter:
            date_filter.name = "Test Date Filter"
            date_filter.type = "filter"
            date_filter.model_id = "ir.filters.group"
            date_filter.date_field = self.env.ref(
                "base_custom_filter.field_ir_filters_group__create_date"
            )
        filter_record = self.filters_obj.search([("name", "=", "Test Date Filter")])
        self.assertEqual(filter_record.name, "Test Date Filter")
        view_dict = self.filters_group_obj.get_view(view_type="search")
        view_content = view_dict.get("arch", b"").decode("utf-8")
        filter_name = "ir_custom_filter_" + str(filter_record.id)
        date_string = (
            f'<filter name="{filter_name}" '
            'string="Test Date Filter" '
            'date="create_date"/>'
        )
        self.assertIn(
            date_string,
            view_content,
            "The date filter is not in the returned view",
        )
