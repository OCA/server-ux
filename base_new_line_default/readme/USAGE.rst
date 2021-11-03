On the view xml file, add the context options, i.e.,

.. code-block:: xml

    <field name="order_line"
        context="{
            'default_src_head': {'name': name},
            'default_src_line': order_line,
            'new_line_default_cols': ['name', 'product_id','product_uom_qty'],
        }
    </field>

* `default_src_head` is the values from header as dict
* `default_src_line` is the one2many field as list
* `default_dest_cols` is to specify only some fields to set default, if not specified, open to all

From the above implementation, when a new record is being added from the UI form view,
the context data is passed in, and default_get() values will use it as default values
