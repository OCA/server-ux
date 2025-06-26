from datetime import datetime, timedelta

from odoo.tests import tagged, users

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class TestAnnouncement(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.general_announcement = cls.env["announcement"].create(
            {
                "name": "Test announcement",
                "content": "<p>Test content for test announcement</p>",
                "is_general_announcement": True,
                "notification_date": datetime.now() + timedelta(days=-1),
                "notification_expiry_date": datetime.now() + timedelta(days=+1),
                "active": True,
            }
        )
        cls.expired_announcement = cls.env["announcement"].create(
            {
                "name": "Test expired announcement",
                "content": "<p>Its gone</p>",
                "is_general_announcement": True,
                "notification_date": datetime.now() + timedelta(days=-2),
                "notification_expiry_date": datetime.now() + timedelta(days=-1),
                "active": True,
            }
        )
        cls.admin_announcement = cls.env["announcement"].create(
            {
                "name": "Test admin only announcement",
                "content": "<p>Test content for admins only</p>",
                "announcement_type": "user_group",
                "user_group_ids": cls.env.ref("base.group_system"),
                "notification_date": datetime.now() + timedelta(days=-1),
                "notification_expiry_date": datetime.now() + timedelta(days=+1),
                "active": True,
            }
        )

    @users("admin")
    def test_announcements_admin(self):
        res = self.env.user.get_announcements()
        announcement_ids = [announcement["id"] for announcement in res["data"]]
        self.assertIn(self.general_announcement.id, announcement_ids)
        self.assertIn(self.admin_announcement.id, announcement_ids)
        self.assertNotIn(self.expired_announcement.id, announcement_ids)

    @users("demo")
    def test_announcements_user(self):
        res = self.env.user.get_announcements()
        announcement_ids = [announcement["id"] for announcement in res["data"]]
        self.assertIn(self.general_announcement.id, announcement_ids)
        self.assertNotIn(self.admin_announcement.id, announcement_ids)
        self.assertNotIn(self.expired_announcement.id, announcement_ids)
