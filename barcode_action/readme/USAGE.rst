Actions must be configured with the following data in the context:
* model: Model where we can find the method (required)
* method: Method to execute (required)
* res_id: Id as base (optional)

The method must return an action. For example

Action example::

    <act_window id="sale_order_find"
                name="Find Sale Order"
                res_model="barcode.action"
                view_mode="form"
                view_type="form"
                context="{'default_model': 'sale.order', 'default_method': 'find_sale_order_by_barcode'}"
                target="new"/>

Python example::

    @api.multi
    def find_sale_order_by_barcode(self, barcode):
        sale_order = self.search([('name', '=', barcode)])
        if not sale_order:
            action = self.env.ref('sale_order_find')
            result = action.read()[0]
            context = safe_eval(result['context'])
            context.update({
                'default_state': 'warning',
                'default_status': _('Sale Order %s cannot be found') % barcode
            })
            result['context'] = json.dumps(context)
            return result
        action = self.env.ref('sale.action_quotations')
        result = action.read()[0]
        res = self.env.ref('sale.view_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = sale_order.id
        return result
