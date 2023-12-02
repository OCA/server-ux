# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase
from odoo.tools import mute_logger

from ..controllers.web_client import WebClient


class TestBaseUserLocale(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ResCompany = cls.env["res.company"]
        cls.ResUsers = cls.env["res.users"]
        cls.CalendarEvent = cls.env["calendar.event"]

        cls.code = "en_US"
        if not cls.env["res.lang"]._lang_get_id(cls.code):
            cls.env["res.lang"].load_lang(cls.code, "English (US)")

        cls.company = cls.ResCompany.create({"name": "Company"})
        cls.company.partner_id.lang = cls.code

        cls.user = cls.ResUsers.with_context(no_reset_password=True).create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": cls.company.id,
                "company_ids": [(4, cls.company.id)],
                "lang": cls.code,
            }
        )

    def test_uninstalled_lang(self):
        uninstalled_lang = (
            self.env["res.lang"]
            .with_context(active_test=True)
            .search([("active", "=", False)], limit=1)
        )
        if uninstalled_lang:
            with self.assertRaises(ValueError):
                self.ResUsers.with_context(no_reset_password=True).create(
                    {
                        "name": "User",
                        "login": "another user",
                        "email": "user@example.com",
                        "company_id": self.company.id,
                        "company_ids": [(4, self.company.id)],
                        "lang": uninstalled_lang.code,
                    }
                )

    def test_date_format(self):
        self.user.env.company = self.user.company_id

        self.assertEqual(
            self.CalendarEvent.with_user(self.user)._get_date_formats()[0], "%m/%d/%Y"
        )
        lang_parameters = WebClient().get_user_lang_parameters(self.user)
        self.assertEqual(lang_parameters, {})

        self.company.date_format = "%d %b %Y"
        self.assertEqual(
            self.CalendarEvent.with_user(self.user)._get_date_formats()[0], "%d %b %Y"
        )
        lang_parameters = WebClient().get_user_lang_parameters(self.user)
        self.assertEqual(lang_parameters, {"date_format": "%d %b %Y"})

        self.user.date_format = "%d/%b/%Y"
        self.assertEqual(
            self.CalendarEvent.with_user(self.user)._get_date_formats()[0], "%d/%b/%Y"
        )
        lang_parameters = WebClient().get_user_lang_parameters(self.user)
        self.assertEqual(lang_parameters, {"date_format": "%d/%b/%Y"})

    def test_time_format(self):
        self.user.env.company = self.user.company_id

        self.assertEqual(
            self.CalendarEvent.with_user(self.user)._get_date_formats()[1], "%H:%M:%S"
        )
        lang_parameters = WebClient().get_user_lang_parameters(self.user)
        self.assertEqual(lang_parameters, {})

        self.company.time_format = "%H.%M.%S"
        self.assertEqual(
            self.CalendarEvent.with_user(self.user)._get_date_formats()[1], "%H.%M.%S"
        )
        lang_parameters = WebClient().get_user_lang_parameters(self.user)
        self.assertEqual(lang_parameters, {"time_format": "%H.%M.%S"})

        self.user.time_format = "%I:%M%p"
        self.assertEqual(
            self.CalendarEvent.with_user(self.user)._get_date_formats()[1], "%I:%M%p"
        )
        lang_parameters = WebClient().get_user_lang_parameters(self.user)
        self.assertEqual(lang_parameters, {"time_format": "%I:%M%p"})

    def test_week_start(self):
        self.user.env.company = self.user.company_id

        lang_parameters = WebClient().get_user_lang_parameters(self.user)
        self.assertEqual(lang_parameters, {})

        self.company.week_start = "4"
        lang_parameters = WebClient().get_user_lang_parameters(self.user)
        self.assertEqual(lang_parameters, {"week_start": 4})

        self.user.week_start = "2"
        lang_parameters = WebClient().get_user_lang_parameters(self.user)
        self.assertEqual(lang_parameters, {"week_start": 2})

    @mute_logger("odoo.addons.base.models.ir_model")
    def test_user_can_write_own_fields(self):
        self.user.env.company = self.user.company_id

        vals = {
            "date_format": "%d/%b/%Y",
            "time_format": "%H.%M.%S",
            "week_start": "1",
            "decimal_point": ".",
            "thousands_sep": ",",
        }

        self.user.with_user(self.user.id).write(vals)

        admin_with_user = self.env.ref("base.user_admin").with_user(self.user.id)
        for field, value in vals.items():
            with self.assertRaises(AccessError, msg=f"failed for field {field}"):
                admin_with_user.write({field: value})
