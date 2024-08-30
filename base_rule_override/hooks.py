# Copyright 2024 Ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    """Set all "is_override" rules to inactive before uninstalling."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.rule"].search([("is_override", "=", True)]).write({"active": False})
