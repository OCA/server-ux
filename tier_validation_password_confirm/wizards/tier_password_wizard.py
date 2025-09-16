from odoo import _, api, fields, models
from odoo.exceptions import AccessDenied, ValidationError


class CommentWizardInherit(models.TransientModel):
    _inherit = "comment.wizard"

    password = fields.Char()
    has_comment = fields.Boolean()
    require_password = fields.Boolean()
    comment = fields.Char(required=False)

    @api.model
    def default_get(self, fields_list):
        """Set default values based on context."""
        defaults = super().default_get(fields_list)
        defaults["has_comment"] = self.env.context.get("comment", False)
        defaults["require_password"] = self.env.context.get("require_password", False)

        return defaults

    def add_comment(self):
        self.ensure_one()
        if self.require_password:
            user = self.env.user
            try:
                credentials = {
                    "login": user.login,
                    "password": self.password,
                    "type": "password",
                }
                user._check_credentials(credentials, {"interactive": True})
                self.review_ids.write({"password_confirmed": True})
            except AccessDenied as e:
                raise ValidationError(_("Incorrect password. Please try again.")) from e

        return super().add_comment()
