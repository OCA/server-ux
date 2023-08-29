# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models

LOG_ARCHIVE_DATE = "archive_date"
LOG_ARCHIVE_UID = "archive_uid"


class Base(models.AbstractModel):
    """
    The base model is inherited by all models.

    Whenever a record has the active field, we save the latest date in which the record
    has been archived, False otherwise. We also save which user did the archiving.
    """

    _inherit = "base"

    @api.model
    def _get_now_date(self):
        """
        :return: datetime.datetime: actual time formated in the way Odoo saves dates
        for base fields, such as write_date or create_date
        """
        now = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        return now.replace(tzinfo=None)

    @api.model
    def _add_magic_fields(self):
        result = super(Base, self)._add_magic_fields()
        if self._log_access and "active" in self._fields:
            self._add_field(
                LOG_ARCHIVE_DATE,
                fields.Datetime(
                    string="Last Archived on", automatic=True, readonly=True
                ),
            )
            self._add_field(
                LOG_ARCHIVE_UID,
                fields.Many2one(
                    comodel_name="res.users",
                    string="Last Archived by",
                    automatic=True,
                    readonly=True,
                ),
            )
        return result

    @api.model_create_multi
    @api.returns("self", lambda value: value.id)
    def create(self, vals_list):
        if self._log_access:
            for vals in vals_list:
                if "active" in vals:
                    archive_date = (
                        False if vals.get("active", False) else self._get_now_date()
                    )
                    archive_uid = self.env.user.id if archive_date else False
                    vals.update(
                        {LOG_ARCHIVE_DATE: archive_date, LOG_ARCHIVE_UID: archive_uid}
                    )
        return super(Base, self).create(vals_list)

    def write(self, vals):
        if (
            self._log_access
            and LOG_ARCHIVE_DATE not in vals
            and "active" in vals
            and not vals.get("active", True)
        ):
            now = self._get_now_date()
            user_id = self.env.user.id
            vals.update({LOG_ARCHIVE_DATE: now, LOG_ARCHIVE_UID: user_id})
        return super(Base, self).write(vals)
