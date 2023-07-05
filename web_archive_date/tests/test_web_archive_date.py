# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base_archive_date.tests.test_base_archive_date import (
    TestBaseArchiveDate,
)


class TestWebArchiveDate(TestBaseArchiveDate):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Models
        cls.company_model = cls.env["res.company"]

        # Instances
        cls.company = cls.company_model.create({"name": "Test Company"})

    def test_01_check_metadata_shown(self):
        """
        Check that the method getting the metadata on a record, once it is archived.
        """
        self.partner.toggle_active()
        metadata = self.partner.get_metadata()
        self.assertEqual(len(metadata), 1, "List should only contain one value.")
        value = metadata[0]
        self.assertTrue(value)
        self.assertTrue(
            "id" in value.keys() and self.partner.id == value.get("id"),
            "Partner ID should be the value of the key ID in the dictionary.",
        )
        self.assertTrue(
            "archive_date" in value.keys() and "archive_uid" in value.keys()
        )
        self.assertEqual(
            value.get("archive_date"),
            self.partner.archive_date,
            "Value shown in the metadata view should be equal to the one set in the partner.",
        )
        self.assertEqual(
            value.get("archive_uid")[0],
            self.partner.archive_uid.id,
            "User ID shown used in the metadata should be the same as the archive_uid value.",
        )

    def test_02_check_metadata_shown_on_model_not_having_active_field(self):
        """
        Check that the method getting the metadata on a record, if the record doesn't
        have the active field.
        """
        c_fields_list = list(self.company._fields)
        self.assertFalse("active" in c_fields_list)
        metadata = self.company.get_metadata()
        self.assertEqual(len(metadata), 1, "List should only contain one value.")
        value = metadata[0]
        self.assertFalse(
            "archive_date" in value.keys(),
            "The Archive Date should not be listed for a model not having the active field.",
        )
        self.assertFalse(
            "archive_uid" in value.keys(),
            "The Archive by should not be listed for a model not having the active field.",
        )
