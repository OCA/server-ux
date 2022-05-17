By default, the cancel confirm will be disabled (to ensure no side effect on other module unit test)

To enable cancel confirm wizard, please add System Parameter (ir.config_parameter) for each extended module.

For example,

* sale_cancel_confirm, add `sale.order.cancel_confirm_disable = False`
* purchase_cancel_confirm, add `purchase.order.cancel_confirm_disable = False`
