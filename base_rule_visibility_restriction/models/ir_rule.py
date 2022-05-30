# 2022 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class IrRule(models.Model):

    _inherit = "ir.rule"

    excluded_group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="ir_rule_excluded_group_rel",
        column1="rule_id",
        column2="gid",
        string="Excluded Groups",
    )

    def _get_rules(self, model_name, mode="read"):
        res = super()._get_rules(model_name, mode)
        if res.sudo().excluded_group_ids:
            # pylint: disable=E8103
            query = """ SELECT r.id FROM ir_rule r JOIN ir_model m ON (r.model_id=m.id)
                    WHERE m.model=%s AND r.active AND r.perm_{mode}
                    AND (r.id IN (SELECT reg.rule_id FROM ir_rule_excluded_group_rel reg
                                  JOIN res_groups_users_rel gu ON (reg.gid=gu.gid)
                                  WHERE gu.uid=%s))
                    ORDER BY r.id
                """.format(
                mode=mode
            )
            self._cr.execute(query, (model_name, self._uid))
            return res - self.browse(row[0] for row in self._cr.fetchall())
        return res
