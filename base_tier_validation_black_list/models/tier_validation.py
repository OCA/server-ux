
from odoo import api, fields, models

class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    @api.model
    def _get_exception_fields(self, extra_domain=None):
        """
        Return Tier Validation Exception field names that matchs custom domain
        taken account blacklist exceptions.
        """
        extra_domain = extra_domain or []
        extra_domain.append(("is_blacklist", "=", False))
        res = super()._get_exception_fields(extra_domain=extra_domain)
        extra_domain.remove(("is_blacklist", "=", False))
        domain =  [
                    ("model_name", "=", self._name),
                    ("company_id", "in", [False] + self._get_company().ids),
                    ("is_blacklist", "=", True),
                    "|",
                    ("group_ids", "in", self.env.user.groups_id.ids),
                    ("group_ids", "=", False),
                    *(extra_domain or []),
                ]
        exception_ids = (self.env["tier.validation.exception"]
            .sudo()
            .search(
                domain
            )
        )
        if exception_ids:
            all_fields_allowed = exception_ids[0].valid_model_field_ids.mapped("name")
            fields_to_add = set(all_fields_allowed) - set(exception_ids.mapped("field_ids.name"))
            fields_allowed = (set(res) - set(exception_ids.mapped("field_ids.name"))) | fields_to_add
            res = list(fields_allowed)
        return res