# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import AccessDenied, ValidationError


class PasswordWizard(models.TransientModel):
    _name = "password.wizard"
    _description = "Password Wizard"

    validate_reject = fields.Char()
    res_model = fields.Char()
    res_id = fields.Integer()
    review_ids = fields.Many2many(comodel_name="tier.review")
    password = fields.Char(required=True)

    def confirm_password(self):
        self.ensure_one()
        user = self.env.user
        try:
            credentials = {
                "login": user.login,
                "password": self.password,
                "type": "password",
            }
            user._check_credentials(credentials, {"interactive": True})
        except AccessDenied as e:
            raise ValidationError(_("Incorrect password. Please try again.")) from e
        rec = self.env[self.res_model].browse(self.res_id)
        self.review_ids.write({"password_confirmed": True})
        if self.validate_reject == "validate":
            rec._validate_tier(self.review_ids)
        if self.validate_reject == "reject":
            rec._rejected_tier(self.review_ids)
        rec._update_counter({"review_deleted": True})
