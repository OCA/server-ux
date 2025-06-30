from lxml import etree

from odoo.tests.common import TransactionCase


class TestBaseModelTodayFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a test model
        cls.test_model = cls.env["ir.model"].create(
            {
                "name": "Test Model",
                "model": "x_test.model",
            }
        )

        cls.model = cls.env["x_test.model"]

        # Create a dummy search view for the test model
        cls.test_model_search_view = cls.env["ir.ui.view"].create(
            {
                "name": "Test Search View",
                "type": "search",
                "model": "x_test.model",
                "arch_base": """
                <search>
                    <field name="create_date"/>
                    <field name="write_date"/>
                </search>
            """,
            }
        )
        cls.search_view = cls.model.with_context().get_view(
            view_id=cls.test_model_search_view.id, view_type="search"
        )
        cls.search_view_arch = etree.fromstring(cls.search_view["arch"])
        cls.created_today_filter = cls.search_view_arch.xpath(
            "//filter[@name='auto_created_today']"
        )
        cls.updated_today_filter = cls.search_view_arch.xpath(
            "//filter[@name='auto_updated_today']"
        )

    def test_001_no_today_filter_injected_for_non_search_view(self):
        """Test that 'Today' filters are not injected into views other than 'search'."""
        form_view = self.model.with_context().get_view(view_type="form")
        self.assertNotIn("auto_created_today", form_view.get("arch"))
        self.assertNotIn("auto_updated_today", form_view.get("arch"))
        self.assertIsNot(form_view["arch"], None, "View arch should not be None.")

    def test_002_view_arch_contains_filters(self):
        """
        Test that the updated search view arch contains the expected filter elements.
        """
        # Verify arch contains filters
        filters = self.search_view_arch.xpath("//filter")
        self.assertGreater(
            len(filters), 0, "No filters found in the updated search view arch."
        )
        self.assertGreaterEqual(
            len(filters),
            2,
            "At least two filters (Created Today, Updated Today) should be present.",
        )
        self.assertFalse(
            len(filters) == 0, "Filters count should not be zero in the search view."
        )

    def test_003_today_filters_injected_correctly_in_search_view(self):
        """Test that 'Today' filters are properly injected into search views."""
        # Check for 'Created Today' filter
        self.assertTrue(
            self.created_today_filter,
            "'Created Today' filter is missing in the search view.",
        )
        self.assertEqual(
            self.created_today_filter[0].tag,
            "filter",
            "'Created Today' is not a 'filter' tag.",
        )
        self.assertEqual(
            self.created_today_filter[0].get("string"),
            "Created Today",
            "'Created Today' filter has an incorrect string attribute.",
        )

        # Check for 'Updated Today' filter
        self.assertTrue(
            self.updated_today_filter,
            "'Updated Today' filter is missing in the search view.",
        )
        self.assertEqual(
            self.updated_today_filter[0].tag,
            "filter",
            "'Updated Today' is not a 'filter' tag.",
        )
        self.assertEqual(
            self.updated_today_filter[0].get("string"),
            "Updated Today",
            "'Updated Today' filter has an incorrect string attribute.",
        )

    def test_004_today_filters_have_correct_domain(self):
        """Test that the domain attribute on 'Today' filters is formatted correctly."""
        # Expected domains
        expected_create_domain = (
            "[('create_date', '>', "
            "(context_today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))]"
        )
        expected_update_domain = (
            "[('write_date', '>', "
            "(context_today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))]"
        )
        # Check domain of 'Created Today'
        self.assertEqual(
            self.created_today_filter[0].get("domain"),
            expected_create_domain,
            "Domain for 'Created Today' filter does not match the expected value.",
        )
        # Check domain of 'Updated Today'
        self.assertEqual(
            self.updated_today_filter[0].get("domain"),
            expected_update_domain,
            "Domain for 'Updated Today' filter does not match the expected value.",
        )
