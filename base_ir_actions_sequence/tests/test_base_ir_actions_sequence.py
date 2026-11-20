from odoo.tests.common import TransactionCase


class TestBaseIrActionsSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env["ir.model"]._get("res.partner")
        cls.report_late = cls.env["ir.actions.report"].create(
            {
                "name": "Report late",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "base_ir_actions_sequence.report_late",
                "binding_model_id": cls.model.id,
                "binding_type": "report",
                "sequence": 20,
            }
        )
        cls.report_early = cls.env["ir.actions.report"].create(
            {
                "name": "Report early",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "base_ir_actions_sequence.report_early",
                "binding_model_id": cls.model.id,
                "binding_type": "report",
                "sequence": 10,
            }
        )

    def test_report_bindings_sequence(self):
        bindings = self.env["ir.actions.actions"]._get_bindings("res.partner")
        report_ids = [report["id"] for report in bindings.get("report", ())]
        self.assertLess(
            report_ids.index(self.report_early.id),
            report_ids.index(self.report_late.id),
        )
