from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """
    Set deprecated value for all existing fields
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    model_obj = env["ir.model"]
    field_obj = env["ir.model.fields"]
    for model in model_obj.search([]):
        all_fields = model._fields.items()
        for field_name, field in all_fields:
            # Only assign for deprecated fields to avoid too many useless searches
            to_assign = bool(field.deprecated)
            if to_assign:
                odoo_field = field_obj.search(
                    [("name", "=", field_name), ("model", "=", model._name)], limit=1
                )
                if odoo_field:
                    odoo_field.write({"deprecated": to_assign})
