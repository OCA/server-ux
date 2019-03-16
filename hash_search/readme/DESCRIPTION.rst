This module allows to search any kind of record through a QR scanner.

In order to configure a model it must inherit `hash.search.mixin`, define
the ZPL2 Label action to use and set the model as a reference. For example::

    class AccountInvoice(models.Model):
        _name = 'account.invoice'
        _inherit = ['account.invoice', 'hash.search.mixin']

        @api.model
        def _get_label_action(self):
            return self.env.ref(
                'hash_search_account_invoice.account_invoice_hash_print_label')

    class HashSearch(models.Model):
        _inherit = 'hash.search'

        @api.model
        def hash_search_models(self):
            res = super().hash_search_models()
            res.append(('account.invoice', 'Invoice'))
            return res

