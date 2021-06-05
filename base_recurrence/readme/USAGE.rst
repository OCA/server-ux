
Supported intervals
===================

* Day
* Month
* End of Next Month
* Quarter
* Semester
* Year



Example
=======

.. code-block:: python

    from odoo import fields, models


    class RecurrenceModel(models.Model):

        _name = "recurrence.model"
        _inherit = ["recurrence.mixin"]
        _description = "A model that implements recurrence"

        _field_last_recurrency_date = "last_recurrency_date"
        _field_next_recurrency_date = "next_recurrency_date"

        last_recurrency_date = fields.Datetime()
        next_recurrency_date = fields.Datetime()
