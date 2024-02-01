# Copyright 2024 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.osv import expression


class TierReview(models.Model):
    _inherit = "tier.review"

    @api.depends("model", "res_id")
    def _compute_res_name(self):
        for record in self:
            if record.res_id and record.model:
                record.res_name = (
                    self.env[record.model].browse(record.res_id).display_name
                )
            else:
                record.res_name = False

    related_model_instance = fields.Reference(
        selection="_selection_related_model_instance",
        compute="_compute_related_model_instance",
        string="Document",
    )
    res_name = fields.Char(
        "Resource Name", compute="_compute_res_name", compute_sudo=True
    )

    @api.depends("res_id", "model")
    def _compute_related_model_instance(self):
        for record in self:
            ref = False
            if record.res_id:
                ref = "{},{}".format(record.model, record.res_id)
            record.related_model_instance = ref

    @api.model
    def _selection_related_model_instance(self):
        models = self.env["tier.definition"].sudo().search([]).mapped("model_id")
        return [(model.model, model.name) for model in models]

    def open_origin(self):
        self.ensure_one()
        vid = self.env[self.model].browse(self.res_id).get_formview_id()
        response = {
            "type": "ir.actions.act_window",
            "res_model": self.model,
            "view_mode": "form",
            "res_id": self.res_id,
            "target": "current",
            "views": [(vid, "form")],
        }
        return response

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        # Rules do not apply to administrator
        if self.env.is_superuser():
            return super(TierReview, self)._search(
                args,
                offset=offset,
                limit=limit,
                order=order,
                count=count,
                access_rights_uid=access_rights_uid,
            )
        # Perform a super with count as False, to have the ids, not a counter
        ids = super(TierReview, self)._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=False,
            access_rights_uid=access_rights_uid,
        )
        if not ids and count:
            return 0
        elif not ids:
            return ids

        super(
            TierReview, self.with_user(access_rights_uid or self._uid)
        ).check_access_rights("read")

        self.flush_model(["model", "res_id"])
        reviews_to_check = []
        for sub_ids in self._cr.split_for_in_conditions(ids):
            self._cr.execute(
                """
                SELECT DISTINCT review.id, review.model, review.res_id
                FROM "%s" review
                WHERE review.id = ANY (%%(ids)s) AND review.res_id != 0"""
                % self._table,
                dict(ids=list(sub_ids)),
            )
            reviews_to_check += self._cr.dictfetchall()

        review_to_documents = {}
        for review in reviews_to_check:
            review_to_documents.setdefault(review["model"], set()).add(review["res_id"])

        allowed_ids = set()
        for doc_model, doc_ids in review_to_documents.items():
            doc_operation = "read"
            DocumentModel = self.env[doc_model].with_user(
                access_rights_uid or self._uid
            )
            right = DocumentModel.check_access_rights(
                doc_operation, raise_exception=False
            )
            if right:
                valid_docs = DocumentModel.browse(doc_ids)._filter_access_rules(
                    doc_operation
                )
                valid_doc_ids = set(valid_docs.ids)
                allowed_ids.update(
                    review["id"]
                    for review in reviews_to_check
                    if review["model"] == doc_model
                    and review["res_id"] in valid_doc_ids
                )

        if count:
            return len(allowed_ids)
        else:
            id_list = [id for id in ids if id in allowed_ids]
            return id_list

    @api.model
    def _read_group_raw(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        # Rules do not apply to administrator
        if not self.env.is_superuser():
            allowed_ids = self._search(domain, count=False)
            if allowed_ids:
                domain = expression.AND([domain, [("id", "in", allowed_ids)]])
            else:
                # force void result if no allowed ids found
                domain = expression.AND([domain, [(0, "=", 1)]])

        return super(TierReview, self)._read_group_raw(
            domain=domain,
            fields=fields,
            groupby=groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
