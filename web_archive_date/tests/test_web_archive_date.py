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
