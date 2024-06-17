
You can override like here

.. code-block:: xml

    <record id="res_config_settings_view_form" model="ir.ui.view">
        <field name="model">res.config.settings</field>
        <field name="priority" eval="200"/>
        <field name="inherit_id" ref="misc_settings.res_config_settings_view_form"/>
        <field name="arch" type="xml">
            <xpath expr="//div[@data-key='misc_settings']" position="inside">
                <h2>My Section</h2>
                <div class="row mt16 o_settings_container" name="my_section">
                    Complete here
                </div>
            </xpath>
        </field>
    </record>
