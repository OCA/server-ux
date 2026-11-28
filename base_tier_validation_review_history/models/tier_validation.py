# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import fields, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    review_history_ids = fields.One2many(
        comodel_name="tier.review",
        inverse_name="res_id",
        string="Review History",
        domain=lambda self: [("model", "=", self._name), ("active", "=", False)],
        context={"active_test": False},
    )

    def _remove_reviews(self):
        """Archive completed reviews configured to keep history; delete the rest."""
        to_archive = self.review_ids.filtered(
            lambda r: r.status in ("approved", "rejected")
            and r.definition_id
            and r.definition_id._keep_review_history_enabled()
        )
        if to_archive:
            to_archive.write({"active": False})
            # Archiving changes no FK/status, so nothing invalidates the caches of
            # review_ids / review_history_ids or of the fields derived from them.
            # need_validation, has_comment, next_review and is_reevaluation_required
            # are computed without @api.depends in base, so modified() cannot flag
            # them either and they have to be invalidated explicitly.
            self.invalidate_recordset(
                [
                    "review_ids",
                    "review_history_ids",
                    "need_validation",
                    "has_comment",
                    "next_review",
                    "is_reevaluation_required",
                ]
            )
            self.modified(["review_ids"])
        return super(
            TierValidation, self.with_context(active_test=True)
        )._remove_reviews()

    def unlink(self):
        # active_test=False so archived history reviews are deleted too, not orphaned.
        self.with_context(active_test=False).mapped("review_ids").unlink()
        return super().unlink()

    def _add_tier_validation_reviews(self, node, params):
        """Render the base reviews block and append the review-history block,
        wrapped in a single root element (the caller expects one node)."""
        review_node = super()._add_tier_validation_reviews(node, params)
        history_str = self.env["ir.qweb"]._render(
            "base_tier_validation_review_history.tier_validation_review_history",
            params,
        )
        wrapper = etree.Element("div")
        wrapper.append(review_node)
        wrapper.append(etree.fromstring(history_str))
        return wrapper
