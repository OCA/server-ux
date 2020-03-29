from odoo import api, fields, models


class MassObjectGroups(models.Model):
    _inherit = "mass.object"

    groups_id = fields.Many2many(
        comodel_name="res.groups",
        relation="mass_group_rel",
        column1="mass_id",
        column2="group_id",
        string="Groups",
    )

    @api.multi
    def create_action(self):
        super(MassObjectGroups, self).create_action()
        self.mapped("ref_ir_act_window_id").sudo().write(
            {"groups_id": [(4, x.id) for x in self.groups_id]}
        )
        return True
