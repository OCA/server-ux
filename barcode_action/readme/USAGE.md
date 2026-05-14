Actions must be configured with the following keys in their context:

- `model`: model where the method can be found (required)
- `method`: method to execute on that model (required)
- `res_id`: record id passed as the base of the method call (optional)

The configured method must return an action. Installing this module
with demo data will install a demo application that allows the system
administrator to find a partner by the internal reference encoded in a
barcode.

Go to *Settings / Find partners* and scan a barcode that contains the
internal reference of an existing partner. As soon as you read the
barcode the system will redirect you to that partner's form view.

Technical implementation of this example:

Action:

    <record id="res_partner_find" model="ir.actions.act_window">
        <field name="name">Find Partner</field>
        <field name="res_model">barcode.action</field>
        <field name="view_mode">form</field>
        <field name="context">{
            'default_model': 'res.partner',
            'default_method': 'find_res_partner_by_ref_using_barcode',
        }</field>
        <field name="target">new</field>
    </record>

    <menuitem id="menu_orders_customers" name="Find partners"
        action="res_partner_find"
        parent="base.menu_administration"/>

Python code:

    import json
    from odoo import models
    from odoo.tools.safe_eval import safe_eval


    class ResPartner(models.Model):
        _inherit = "res.partner"

        def find_res_partner_by_ref_using_barcode(self, barcode):
            partner = self.search([("ref", "=", barcode)], limit=1)
            if not partner:
                xmlid = "barcode_action.res_partner_find"
                action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
                context = safe_eval(action["context"])
                context.update(
                    {
                        "default_state": "warning",
                        "default_status": self.env._(
                            "Partner with Internal Reference %s cannot be found",
                            barcode,
                        ),
                    }
                )
                action["context"] = json.dumps(context)
                return action
            xmlid = "base.action_partner_form"
            action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
            res = self.env.ref("base.view_partner_form", False)
            action["views"] = [(res and res.id or False, "form")]
            action["res_id"] = partner.id
            return action
