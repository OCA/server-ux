# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request, route


class SwitchController(http.Controller):
    @route('/easy_switch_user/switch', type='json', auth="none")
    def switch(self, login, password):
        uid = request.session.authenticate(request.db, login, password)
        if uid is False:
            raise Exception('Login Failed')
