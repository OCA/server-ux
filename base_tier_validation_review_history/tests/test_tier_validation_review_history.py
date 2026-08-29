# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests.common import Form

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


class TestTierValidationReviewHistory(CommonTierValidation):
    def _reject_and_restart(self, record):
        record.reject_tier()
        review = record.review_ids
        record.restart_validation()
        return review

    # --- Resolution of the effective "keep history" setting -----------------

    def test_definition_keep_archives(self):
        """Definition set to 'keep' -> completed review archived on restart."""
        self.tier_definition.keep_review_history = "keep"
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        review = self._reject_and_restart(record)
        self.assertFalse(review.active)
        self.assertEqual(review.status, "rejected")
        self.assertFalse(record.review_ids)
        self.assertEqual(record.review_history_ids, review)
        # Archiving must refresh review_ids-dependent computes (else the buttons
        # and reviews panel would not display, as validation_status stays "rejected").
        self.assertEqual(record.validation_status, "no")
        self.assertTrue(record.need_validation)
        # A fresh cycle keeps the archived review separate from the new one.
        self.test_record.with_user(self.test_user_2.id).request_validation()
        self.assertEqual(record.review_history_ids, review)

    def test_definition_no_keep_overrides_company(self):
        """Definition 'no_keep' overrides an enabled company default -> deleted."""
        self.tier_definition.company_id = self.env.company
        self.env.company.tier_validation_keep_review_history = True
        self.tier_definition.keep_review_history = "no_keep"
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        self._reject_and_restart(record)
        self.assertFalse(record.review_ids)
        self.assertFalse(record.review_history_ids)

    def test_company_default_keep_inherited(self):
        """Company default 'keep' + empty definition -> archived (inherit)."""
        self.tier_definition.company_id = self.env.company
        self.env.company.tier_validation_keep_review_history = True
        # definition keep_review_history left empty
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        review = self._reject_and_restart(record)
        self.assertFalse(review.active)
        self.assertEqual(record.review_history_ids, review)

    def test_global_definition_inherits_company_default(self):
        """Definition without company (cross-company) -> inherits env.company."""
        self.tier_definition.company_id = False
        self.env.company.tier_validation_keep_review_history = True
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        review = self._reject_and_restart(record)
        self.assertFalse(review.active)
        self.assertEqual(record.review_history_ids, review)

    def test_company_default_off_deletes(self):
        """Company default off + empty definition -> deleted (base behavior)."""
        self.tier_definition.company_id = self.env.company
        self.env.company.tier_validation_keep_review_history = False
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        self._reject_and_restart(record)
        self.assertFalse(record.review_ids)
        self.assertFalse(record.review_history_ids)

    # --- Reset paths --------------------------------------------------------

    def test_pending_review_deleted(self):
        """Pending (never acted on) reviews are deleted even when keeping."""
        self.tier_definition.keep_review_history = "keep"
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        record.restart_validation()
        self.assertFalse(record.review_ids)
        self.assertFalse(record.review_history_ids)

    def test_reset_to_cancel_archives_completed(self):
        """The write reset path (confirm -> cancel) archives completed reviews."""
        self.tier_definition.keep_review_history = "keep"
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        record.validate_tier()
        approved_review = record.review_ids
        record.action_confirm()
        record.write({"state": "cancel"})
        self.assertFalse(record.review_ids)
        archived = record.review_history_ids
        self.assertEqual(archived, approved_review)
        self.assertEqual(archived.status, "approved")

    def test_mixed_rules_archive_and_delete(self):
        """One reset, two rules: keep archived, no_keep deleted."""
        self.tier_definition.keep_review_history = "keep"
        no_keep_def = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "sequence": 40,
                "keep_review_history": "no_keep",
                "name": "Rule without history",
            }
        )
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        self.assertEqual(len(record.review_ids), 2)
        record.reject_tier()
        record.restart_validation()
        self.assertFalse(record.review_ids)
        archived = record.review_history_ids
        self.assertEqual(archived.definition_id, self.tier_definition)
        self.assertNotIn(no_keep_def, archived.definition_id)
        self.assertEqual(len(archived), 1)

    def test_deleted_definition_review_is_removed(self):
        """A completed review whose definition was deleted must not break the reset.

        definition_id is ondelete="set null", so there is no rule left to resolve;
        the review is removed like before the module."""
        self.tier_definition.keep_review_history = "keep"
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        record.reject_tier()
        review = record.review_ids
        self.tier_definition.unlink()
        self.assertFalse(review.definition_id)
        record.restart_validation()
        self.assertFalse(review.exists())
        self.assertFalse(record.review_history_ids)

    def test_history_excludes_other_model_reviews(self):
        """res_id is a Many2oneReference, so only the domain keeps models apart."""
        self.tier_definition.keep_review_history = "keep"
        foreign_review = self.env["tier.review"].create(
            {
                "model": self.test_model_2._name,
                "res_id": self.test_record.id,
                "definition_id": self.tier_definition.id,
                "status": "approved",
                "active": False,
            }
        )
        self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        review = self._reject_and_restart(record)
        self.assertEqual(record.review_history_ids, review)
        self.assertNotIn(foreign_review, record.review_history_ids)

    def test_record_reference(self):
        """record_reference links to the document and tolerates stale models."""
        review = self.env["tier.review"].create(
            {
                "model": self.test_model._name,
                "res_id": self.test_record.id,
                "definition_id": self.tier_definition.id,
            }
        )
        self.assertEqual(review.record_reference, self.test_record)
        # History rows can outlive their model (module uninstalled).
        review.model = "no.longer.installed"
        self.assertFalse(review.record_reference)

    def test_host_unlink_removes_archived_reviews(self):
        """Deleting the host record deletes all reviews, incl. archived history."""
        self.tier_definition.keep_review_history = "keep"
        record_to_delete = self.test_model.create({"test_field": 2.5})
        record_to_delete.with_user(self.test_user_2.id).request_validation()
        record = record_to_delete.with_user(self.test_user_1.id)
        record.reject_tier()
        record.restart_validation()
        archived = record.review_history_ids
        self.assertEqual(len(archived), 1)
        record_to_delete.unlink()
        self.assertFalse(archived.exists())

    def test_history_block_injected_in_form_view(self):
        """The review-history block is injected into the document form view.

        Uses test_record_2 (auto-injected, _tier_validation_manual_config=False).
        Exercises _add_tier_validation_reviews (QWeb render + <div> wrap) and the
        review_history_ids field so a template typo or render error is caught at
        view-build time instead of only in the browser."""
        with Form(self.test_record_2) as f:
            form = etree.fromstring(f._view["arch"])
        self.assertTrue(form.xpath("//field[@name='review_history_ids']"))
