# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

from ..controllers.web_client import WebClient


class TestBaseUserLocale(TransactionCase):
    def setUp(self):
        super().setUp()

        self.ResCompany = self.env["res.company"]
        self.ResUsers = self.env["res.users"]
        self.CalendarEvent = self.env["calendar.event"]

    def test_date_format(self):
        company = self.ResCompany.create({"name": "Company"})
        user = self.ResUsers.with_context(no_reset_password=True).create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "lang": "en_US",
            }
        )

        self.assertEqual(
            self.CalendarEvent.with_user(user)._get_date_formats()[0], "%B-%d-%Y"
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
                "lang": "en_US",
            }
        )

        self.assertEqual(
            self.CalendarEvent.with_user(user)._get_date_formats()[1], "%I-%M %p"
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
                "lang": "en_US",
            }
        )

        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {})

        company.week_start = "4"
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {"week_start": 4})

        user.week_start = "2"
        lang_parameters = WebClient().get_user_lang_parameters(user)
        self.assertEqual(lang_parameters, {"week_start": 2})
