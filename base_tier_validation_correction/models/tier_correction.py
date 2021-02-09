# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TierCorrection(models.Model):
    _name = "tier.correction"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Tier Review Correction"
    _order = "id desc"

    name = fields.Char(
        string="Description",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="On Model",
        domain=lambda self: [
            (
                "model",
                "in",
                self.env["tier.definition"]._get_tier_validation_model_names(),
            )
        ],
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    model = fields.Char(related="model_id.model", index=True, store=True)
    correction_type = fields.Selection(
        selection=[
            ("reviewer", "Reassign Reviewer(s)"),
        ],
        string="Correction Type",
        default="reviewer",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    search_name = fields.Char(
        string="Name Search",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    old_reviewer_ids = fields.Many2many(
        comodel_name="res.users",
        relation="tier_correction_old_reviewer_rel",
        string="Original Reviewer(s)",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Find documents with tier reviews matching some reviewers",
    )
    new_reviewer_ids = fields.Many2many(
        comodel_name="res.users",
        relation="tier_correction_new_reviewer_rel",
        string="Reassign Reviewer(s)",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Reassign these reviewers to the tier reviews of the found document",
    )
    item_ids = fields.One2many(
        comodel_name="tier.correction.item",
        inverse_name="correction_id",
        readonly=True,
        states={"draft": [("readonly", False)], "prepare": [("readonly", False)]},
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("prepare", "Preparing"),
            ("done", "Corrected"),
            ("cancel", "Cancelled"),
            ("revert", "Reverted"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        tracking=1,
        default="draft",
    )
    reference = fields.Char(
        string="Affected Documents",
        compute="_compute_reference",
        store=True,
    )
    date_schedule_correct = fields.Datetime(
        string="Scheduled Correction Date",
        readonly=True,
        states={"draft": [("readonly", False)], "prepare": [("readonly", False)]},
        copy=False,
    )
    date_actual_correct = fields.Datetime(
        string="Actual Correction Date",
        readonly=True,
        copy=False,
    )
    date_schedule_revert = fields.Datetime(
        string="Scheduled Revert Date",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "prepare": [("readonly", False)],
            "done": [("readonly", False)],
        },
        copy=False,
    )
    date_actual_revert = fields.Datetime(
        string="Actual Revert Date",
        readonly=True,
        copy=False,
    )

    @api.constrains("date_schedule_correct", "date_schedule_revert")
    def _check_date(self):
        """ Correct Date < Revert Date """
        for rec in self:
            now = fields.Datetime.now()
            correct = rec.date_schedule_correct or now
            revert = rec.date_schedule_revert or correct or now
            if not (correct <= revert):
                raise ValidationError(_("Revert Date should be after Correct Date"))

    def search_document(self):
        for rec in self:
            rec.item_ids.unlink()
            if rec.correction_type == "reviewer":
                doc_domain = [("review_ids.status", "=", "pending")]
                review_domain = [("status", "=", "pending")]
                if rec.search_name:
                    doc_ids = self.env[rec.model].name_search(rec.search_name)
                    doc_domain += [("id", "in", list(dict(doc_ids).keys()))]
                if rec.old_reviewer_ids:
                    doc_domain += [
                        ("review_ids.reviewer_ids", "in", rec.old_reviewer_ids.ids)
                    ]
                    review_domain += [("reviewer_ids", "in", rec.old_reviewer_ids.ids)]
                items = []
                for doc in self.env[rec.model].search(doc_domain):
                    review_ids = doc.review_ids.filtered_domain(review_domain).ids
                    items.append(
                        (
                            0,
                            0,
                            {
                                "res_model": doc._name,
                                "res_id": doc.id,
                                "resource_ref": "{},{}".format(doc._name, doc.id),
                                "reference": doc.display_name,
                                "new_reviewer_ids": [(6, 0, rec.new_reviewer_ids.ids)],
                                "review_ids": [(6, 0, review_ids)],
                            },
                        )
                    )
                rec.write({"item_ids": items})

    @api.depends("item_ids")
    def _compute_reference(self):
        for rec in self:
            rec.reference = ", ".join(
                rec.item_ids.filtered("reference").mapped("reference")
            )

    def do_correct(self):
        for rec in self:
            if rec.state != "prepare":
                raise ValidationError(
                    _("Correction is allowed on state = 'prepare' only")
                )
            if rec.correction_type == "reviewer":
                rec.item_ids.correct()
        self.write({"date_actual_correct": fields.Datetime.now()})

    def do_revert(self):
        for rec in self:
            if rec.state != "done":
                raise ValidationError(_("Correction is allowed on state = 'done' only"))
            if rec.correction_type == "reviewer":
                rec.item_ids.revert()
        self.write({"date_actual_revert": fields.Datetime.now()})

    def action_draft(self):
        self.mapped("item_ids").unlink()
        self.write({"state": "draft"})

    def action_prepare(self):
        self.search_document()
        self.write({"state": "prepare"})

    def action_done(self):
        self.do_correct()
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_revert(self):
        self.do_revert()
        self.write({"state": "revert"})

    def view_scheduled_action(self):
        self.ensure_one()
        action = self.env.ref("base.ir_cron_act")
        result = action.read()[0]
        cron = self.env.ref("base_tier_validation_correction.tier_correction_scheduler")
        result["domain"] = [("id", "in", cron.id)]
        return result

    def _tier_correction_auto_run(self):
        # To correct
        to_correct = self.search(
            [
                ("state", "=", "prepare"),
                ("date_schedule_correct", "!=", False),
                ("date_schedule_correct", "<=", fields.Datetime.now()),
            ]
        )
        to_correct.action_done()
        _logger.info("Tier Correction - Correction: %s " % to_correct)
        # To revert
        to_revert = self.search(
            [
                ("state", "=", "done"),
                ("date_schedule_revert", "!=", False),
                ("date_schedule_revert", "<=", fields.Datetime.now()),
            ]
        )
        to_revert.action_revert()
        _logger.info("Tier Correction - Reversion: %s " % to_revert)


class TierCorrectionItem(models.Model):
    _name = "tier.correction.item"
    _description = "Tier Correction Detail"

    correction_id = fields.Many2one(
        comodel_name="tier.correction",
        index=True,
    )
    res_model = fields.Char(readonly=True)
    res_id = fields.Integer(readonly=True)
    resource_ref = fields.Reference(
        string="Resource",
        selection=lambda self: [
            (model.model, model.name) for model in self.env["ir.model"].search([])
        ],
        readonly=True,
    )
    reference = fields.Char(readonly=True)
    new_reviewer_ids = fields.Many2many(
        comodel_name="res.users",
        relation="tier_correction_item_new_reviewer_rel",
        string="New Reviewers",
        help="These reviewers will overwrite the existing reviewer_ids in tier.review",
    )
    review_ids = fields.Many2many(
        comodel_name="tier.review",
        string="Affected Tier Reviews",
        help="Tier reivews that will be affected by this correction.",
    )

    def _notify_reviewer_change(self, ttype="correct"):
        self.ensure_one()
        post = "message_post"
        if hasattr(self.resource_ref, post):
            tier_reviews = self.review_ids
            reviews = ", ".join(tier_reviews.filtered("name").mapped("name"))
            reviewers = ", ".join(
                tier_reviews.reviewer_ids.filtered("name").mapped("name")
            )
            message = _("The Correction '%s', corrrected reviewers on '%s' to '%s'") % (
                self.correction_id.name,
                reviews,
                reviewers,
            )
            if ttype == "revert":
                message = _(
                    "The Correction '%s', reverted reviewers on '%s' back to '%s'"
                ) % (self.correction_id.name, reviews, reviewers)
            getattr(self.resource_ref, post)(
                subtype_xmlid=(
                    "base_tier_validation_correction.mt_tier_validation_correction"
                ),
                body=message,
            )

    def correct(self):
        for item in self:
            # Only pending reviews will gets updated
            item.review_ids.filtered(lambda l: l.status == "pending").write(
                {"reviewer_ids": [(6, 0, item.new_reviewer_ids.ids)]}
            )
            item._notify_reviewer_change("correct")

    def revert(self):
        for item in self:
            for review in item.review_ids.filtered(lambda l: l.status == "pending"):
                review.reviewer_ids = review._get_reviewers()
            item._notify_reviewer_change("revert")
