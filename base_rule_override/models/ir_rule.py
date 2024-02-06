# Copyright 2024 Ooops404
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, tools
from odoo.osv import expression
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval


class IrRule(models.Model):
    _inherit = "ir.rule"

    is_override = fields.Boolean(
        string="Override",
        help="Unlike other rules, override rules "
        "must be passed in order to allow visibility to the record",
    )

    def _get_failing(self, for_records, mode="read"):
        res = super()._get_failing(for_records, mode)
        if res:
            return res
        Model = for_records.browse(()).sudo()
        eval_context = self._eval_context()
        override_rules = self._get_rules(Model._name, mode=mode).sudo()

        def is_failing(r, ids=for_records.ids):
            dom = safe_eval(r.domain_force, eval_context) if r.domain_force else []
            return Model.search_count(
                expression.AND([[("id", "in", ids)], expression.normalize_domain(dom)])
            ) < len(ids)

        return override_rules.filtered(lambda r: is_failing(r)).with_user(self.env.user)

    def _get_rules(self, model_name, mode="read"):
        """
        Return non-override rules by default
        """
        res = super()._get_rules(model_name, mode).sudo()
        if self.env.context.get("get_rule_override"):
            res = res.filtered(lambda x: x.is_override)
        else:
            res = res.filtered(lambda x: not x.is_override)
        return res.with_user(self.env.user)

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        """
        Override domains are in AND with other domains
        regardless of groups
        """
        res = super()._compute_domain(model_name, mode)
        override_rules = self.with_context(get_rule_override=True)._get_rules(
            model_name, mode=mode
        )
        if not override_rules:
            return res

        # browse user and rules as SUPERUSER_ID to avoid access errors!
        eval_context = self._eval_context()
        override_domains = []
        for rule in override_rules.sudo():
            # evaluate the domain for the current user
            dom = (
                safe_eval(rule.domain_force, eval_context) if rule.domain_force else []
            )
            dom = expression.normalize_domain(dom)
            override_domains.append(dom)
        if res is None:
            return expression.AND(override_domains)
        return expression.AND(override_domains + [res])
