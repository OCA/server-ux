=======================
Barcode action launcher
=======================

This module allows to use barcodes as launchers of actions.

The action will launch a function that uses the barcode in order to return an action.

Usage
=====
Actions must be configured with the following data in the context:
* model: Model where we can find the method (required)
* method: Method to execute (required)
* res_id: Id as base (optional)

The method must return an action. Installing this module with demo data will
install a demo application that allows the system administrator to find a
partner by the external reference encoded in a barcode.

Go to *Settings / Find partners* and scan a barcode that contains the
internal reference of an existing partner. As soon as you read the barcode
the system will redirect you to that partner's form view.

Technical implementation of this example:

Action::

        <act_window id="res_partner_find"
            name="Find Partner"
            res_model="barcode.action"
            view_mode="form"
            view_type="form"
            context="{'default_model': 'res.partner', 'default_method': 'find_res_partner_by_ref_using_barcode'}"
            target="new"/>

        <menuitem id="menu_orders_customers" name="Find partners"
            action="res_partner_find"
            parent="base.menu_administration"/>

Python code::

    import json
    from odoo import api, models, _
    from odoo.tools.safe_eval import safe_eval


    class ResPartner(models.Model):
        _inherit = 'res.partner'

        @api.multi
        def find_res_partner_by_ref_using_barcode(self, barcode):
            partner = self.search([('ref', '=', barcode)], limit=1)
            if not partner:
                action = self.env.ref('res_partner_find')
                result = action.read()[0]
                context = safe_eval(result['context'])
                context.update({
                    'default_state': 'warning',
                    'default_status': _('Partner with Internal Reference '
                                        '%s cannot be found') % barcode
                })
                result['context'] = json.dumps(context)
                return result
            action = self.env.ref('base.action_partner_form')
            result = action.read()[0]
            res = self.env.ref('base.view_partner_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = partner.id
            return result

Contributors
============
* Enric Tobella <etobella@creublanca.es>
* Jordi Ballester <jordi.ballester@eficent.com>
