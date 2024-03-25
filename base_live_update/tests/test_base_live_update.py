# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestBaseLiveUpdate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.notification = cls.env.ref(
            "base_live_update.live_update_notification_partner"
        )
        cls.partner = cls.env.ref("base.user_demo").partner_id

    def test_base_live_update(self):
        """
        Test that live.update.notification records decide if live update
        notifications are sent
        """
        self.notification.active = False
        with patch.object(self.partner.__class__, "_live_update") as mock_live_update:
            self.partner.name = "test"
            self.partner.flush_recordset()
            mock_live_update.assert_not_called()
        self.notification.active = True
        with patch.object(self.partner.__class__, "_live_update") as mock_live_update:
            self.partner.name = "test2"
            self.partner.flush_recordset()
            self.assertTrue(mock_live_update.called)
            mock_live_update.assert_called_once_with(
                "write",
                {
                    "name": "test2",
                    "display_name": "YourCompany, test2",
                    "__ids": self.partner.ids,
                },
            )
        self.notification.unlink()
        with patch.object(self.partner.__class__, "_live_update") as mock_live_update:
            self.partner.name = "test"
            self.partner.flush_recordset()
            mock_live_update.assert_not_called()
