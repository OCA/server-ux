# Copyrithg 2020 Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestServerActionDomain(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_1, cls.partner_2 = cls.env["res.partner"].create(
            [
                {
                    "name": "Partner with Country",
                    "country_id": cls.env.ref("base.be").id,
                },
                {
                    "name": "Partner without Country",
                    "country_id": False,
                },
            ]
        )
        cls.server_action = cls.env["ir.actions.server"].create(
            {
                "name": "Anonymize",
                "state": "code",
                "code": "if records: records.write({'name': '** Anonymized **'})",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "domain": "[('country_id', '=', False)]",
            }
        )
        cls.server_action_single = cls.server_action.copy(
            {
                "code": "if record: record.write({'name': '** Anonymized **'})",
            }
        )

    def test_00_action_with_domain(self):
        self.server_action.with_context(
            active_model="res.partner",
            active_ids=(self.partner_1 | self.partner_2).ids,
        ).run()
        self.assertEqual(self.partner_1.name, "Partner with Country")
        self.assertEqual(self.partner_2.name, "** Anonymized **")

    def test_01_action_without_domain(self):
        self.server_action.domain = False
        self.server_action.with_context(
            active_model="res.partner",
            active_ids=(self.partner_1 | self.partner_2).ids,
        ).run()
        self.assertEqual(self.partner_1.name, "** Anonymized **")
        self.assertEqual(self.partner_2.name, "** Anonymized **")

    def test_02_action_single(self):
        self.server_action_single.with_context(
            active_model="res.partner",
            active_id=self.partner_1.id,
        ).run()
        self.assertEqual(self.partner_1.name, "Partner with Country")
        self.server_action_single.with_context(
            active_model="res.partner",
            active_id=self.partner_2.id,
        ).run()
        self.assertEqual(self.partner_2.name, "** Anonymized **")

    def test_03_action_single_without_domain(self):
        self.server_action_single.domain = False
        self.server_action_single.with_context(
            active_model="res.partner",
            active_id=self.partner_1.id,
        ).run()
        self.assertEqual(self.partner_1.name, "** Anonymized **")
