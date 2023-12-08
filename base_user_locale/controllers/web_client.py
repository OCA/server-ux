# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.web.controllers.webclient import WebClient


class WebClient(WebClient):
    def get_user_lang_parameters(self, user):
        res = {}
        date_format = user.date_format or user.env.company.date_format
        if date_format:
            res.update({"date_format": date_format})
        time_format = user.time_format or user.env.company.time_format
        if time_format:
            res.update({"time_format": time_format})
        week_start = user.week_start or user.env.company.week_start
        if week_start:
            res.update({"week_start": int(week_start)})  # NOTE: WebClient needs int
        point_decimal = user.decimal_point or user.env.company.decimal_point
        if point_decimal:
            res.update({"decimal_point": point_decimal})
        sep_thousands = user.thousands_sep or user.env.company.thousands_sep
        if sep_thousands:
            res.update({"thousands_sep": sep_thousands})
        return res

    @http.route(
        "/web/webclient/translations/<string:unique>",
        type="http",
        auth="public",
        cors="*",
    )
    def translations(self, unique, mods=None, lang=None):
        res = super().translations(unique, mods, lang)
        if "uid" in request.session:
            ensure_db()
            user = request.env["res.users"].sudo().browse(request.session["uid"])
            json_data = res.get_data()
            data = json.loads(json_data)
            data["lang_parameters"].update(self.get_user_lang_parameters(user))
            res.set_data(json.dumps(data))
        return res
