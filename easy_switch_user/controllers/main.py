# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo.http import request, route
from odoo.service import security

from odoo.addons.web.controllers.main import Home

_logger = logging.getLogger(__name__)


class WebHome(Home):
    @route(["/web/become", "/web/become/<int:uid>"])
    def switch_to_admin(self, uid=None):
        """Inheritance to switch to a user different from the superuser user"""
        if uid is None or not request.env.user._is_system():
            return super().switch_to_admin()
        user_obj = request.env["res.users"]
        user = user_obj.browse(uid)
        request.session.uid = user.id
        user_obj.clear_caches()
        request.session.session_token = security.compute_session_token(
            request.session,
            request.env,
        )
        _logger.info(
            "User `%s` (#%d) connected as user `%s` (#%d)",
            request.env.user.login,
            request.env.uid,
            user.login,
            user.id,
        )
        return request.redirect(self._login_redirect(uid))
