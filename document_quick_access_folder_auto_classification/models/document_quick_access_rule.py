# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, models

try:
    from odoo.addons.queue_job.job import job
except ImportError:
    job = lambda *args, **kwargs: lambda func: func  # noqa: E731

_logger = logging.getLogger(__name__)


class DocumentQuickAccessRule(models.Model):
    _inherit = "document.quick.access.rule"

    @api.model
    def read_code(self, code):
        try:
            return super().read_code(code)
        except Exception:
            if self.env.context.get("no_raise_document_access", False):
                return False
            raise
