# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import SavepointCase


class TestBaseArchiveDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Models
        cls.partner_model = cls.env["res.partner"]

        # Instances
        cls.partner = cls.partner_model.create({"name": "Test Partner"})

    def test_01_archive_partner_timestamp(self):
        """
        Check that the technical field exists and check for the timestamp once the
        partner is archived.
        """
        self.assertTrue(self.partner.active)
        self.assertTrue("archive_date" in self.partner._fields)
        self.partner.toggle_active()
        now = fields.Datetime.context_timestamp(
            self.partner, fields.Datetime.now()
        ).replace(tzinfo=None)
        self.assertEqual(
            self.partner.archive_date, now, "Archive Date should be equal to now."
        )
