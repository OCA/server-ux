In the model/s that you want to use, you must add `l10n_multi_country.mixin` as inheritance and then add the tag `country = 'US'` (with the code of the country we need) to the fields we want.

When a field with a `country` tag is added to any view, it will be shown or hidden according to the linked company.

An example would be this:

.. code:: python

    Class ResCompany(models.Model):
        _name = 'res.company'
        _inherit = ['res.company', 'l10n_multi_country.mixin']

        custom_us_field = fields.Char(
            string="Custom us field",
            country='US'
        )
