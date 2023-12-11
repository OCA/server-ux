# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase

from ..controllers.web_client import WebClient


class TestBaseUserLocale(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ResCompany = cls.env["res.company"]
        cls.ResUsers = cls.env["res.users"]
        cls.CalendarEvent = cls.env["calendar.event"]
        cls.code = "en_US"
        lang_name = "English (US)"
        if not cls.env["res.lang"]._lang_get_id(cls.code):
            cls.env["res.lang"].load_lang(cls.code, lang_name)

    def test_uninstalled_lang(self):
        company = self.ResCompany.create({"name": "Company"})
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
                        "login": "user",
                        "email": "user@example.com",
                        "company_id": company.id,
                        "company_ids": [(4, company.id)],
                        "lang": uninstalled_lang.code,
                    }
                )

    def test_date_format(self):
        company = self.ResCompany.create({"name": "Company"})
        user = self.ResUsers.with_context(no_reset_password=True).create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "lang": self.code,
            }
        )
        company.partner_id.lang = self.code
        user.env.company = user.company_id

        self.assertEqual(
            self.CalendarEvent.with_user(user)._get_date_formats()[0], "%m/%d/%Y"
        )
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {})

        company.date_format = "%d %b %Y"
        self.assertEqual(
            self.CalendarEvent.with_user(user)._get_date_formats()[0], "%d %b %Y"
        )
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {"date_format": "%d %b %Y"})

        user.date_format = "%d/%b/%Y"
        self.assertEqual(
            self.CalendarEvent.with_user(user)._get_date_formats()[0], "%d/%b/%Y"
        )
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {"date_format": "%d/%b/%Y"})

    def test_time_format(self):
        company = self.ResCompany.create({"name": "Company"})
        user = self.ResUsers.with_context(no_reset_password=True).create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "lang": self.code,
            }
        )
        company.partner_id.lang = self.code
        user.env.company = user.company_id

        self.assertEqual(
            self.CalendarEvent.with_user(user)._get_date_formats()[1], "%H:%M:%S"
        )
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {})

        company.time_format = "%H.%M.%S"
        self.assertEqual(
            self.CalendarEvent.with_user(user)._get_date_formats()[1], "%H.%M.%S"
        )
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {"time_format": "%H.%M.%S"})

        user.time_format = "%I:%M%p"
        self.assertEqual(
            self.CalendarEvent.with_user(user)._get_date_formats()[1], "%I:%M%p"
        )
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {"time_format": "%I:%M%p"})

    def test_week_start(self):
        company = self.ResCompany.create({"name": "Company"})
        user = self.ResUsers.with_context(no_reset_password=True).create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "lang": self.code,
            }
        )
        company.partner_id.lang = self.code
        user.env.company = user.company_id

        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {})

        company.week_start = "4"
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {"week_start": 4})

        user.week_start = "2"
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {"week_start": 2})
