Example of class:

.. code:: python

  class MyWizard(models.TransientModel):
      _name = 'my.wizard'
      _inherit = ['multi.step.wizard.mixin']

      project_id = fields.Many2one(
          comodel_name='project.project',
          name="Project",
          required=True,
          ondelete='cascade',
          default=lambda self: self._default_project_id(),
      )
      name = fields.Char()
      field1 = fields.Char()
      field2 = fields.Char()
      field3 = fields.Char()

      @api.model
      def _selection_state(self):
          return [
              ('start', 'Start'),
              ('configure', 'Configure'),
              ('custom', 'Customize'),
              ('final', 'Final'),
          ]

      @api.model
      def _default_project_id(self):
          return self.env.context.get('active_id')

      def state_exit_start(self):
          self.state = 'configure'

      def state_exit_configure(self):
          self.state = 'custom'

      def state_exit_custom(self):
          self.state = 'final'

Example of view (note the mode, must be primary):

.. code:: xml

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

    <record id="my_wizard_form" model="ir.ui.view">
      <field name="name">my.wizard.form</field>
      <field name="model">my.wizard</field>
      <field name="mode">primary</field>
      <field name="inherit_id" ref="multi_step_wizard.multi_step_wizard_form"/>
      <field name="arch" type="xml">
        <xpath expr="//footer" position="before">
          <h1>
            <field name="name"
                  attrs="{'readonly': [('state', '!=', 'start')]}"
                  class="oe_inline"
                  placeholder="Name"/>
          </h1>
          <group name="configure" attrs="{'invisible': [('state', '!=', 'configure')]}">
            <group>
              <field name="field1"/>
              <field name="field2"/>
            </group>
          </group>
          <group name="custom" attrs="{'invisible': [('state', '!=', 'custom')]}">
            <group>
              <field name="field3"/>
            </group>
          </group>
          <div name="final" attrs="{'invisible': [('state', '!=', 'final')]}">
            <p>The project is now configured.</p>
          </div>
        </xpath>
      </field>
    </record>

    <record id="open_my_wizard" model="ir.actions.act_window">
        <field name="name">My Wizard</field>
        <field name="res_model">my.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="binding_model_id" ref="project.model_project_project" />
        <field name="binding_view_types">form</field>
    </record>
  </odoo>
