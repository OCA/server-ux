from odoo import fields, models


class ServerActionWizard(models.TransientModel):
    _name = "server.action.wizard"
    _description = "Wizard to run server actions with parameters"

    model_id = fields.Many2one("ir.model", string="Model", required=True)
    server_action_id = fields.Many2one(
        "ir.actions.server",
        string="Server Action",
        required=True,
        domain="[('model_id', '=', model_id), ('can_run_from_wizard', '=', True)]",
    )

    param_date_start = fields.Char("Date Start")
    param_date_end = fields.Char("Date End")
    param_1 = fields.Char("Parameter 1")
    param_2 = fields.Char("Parameter 2")

    def run_server_action(self):
        ctx_add = {
            "param_1": self.param_1,
            "param_2": self.param_2,
            "param_3": self.param_3,
            "param_4": self.param_4,
        }
        self.server_action_id.with_context(**ctx_add).run()
