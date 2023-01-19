#. By setting **deprecated=True** to a declared field, the Odoo field will inherit the value and it will be stored at the database level.
#. For instance:
    #. If we have the following field: test_field = fields.Boolean(deprecated=True).
    #. By looking at the instance that saves the information of the Python field on the **ir.model.fields** model, the deprecated attribute will be set there, just like copied, store, computed, among others.
