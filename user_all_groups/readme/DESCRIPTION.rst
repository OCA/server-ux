This module extends the base Odoo module, adding a new field on user form view
named 'Member of all Groups'.

If checked, the user will belong to all the groups (``res.groups``) and if a new module
is installed, the user(s) will automatically belong to the new created groups.

This feature can be interesting:

- on production, if you have some 'admin' users that want to access all features.

- in a development environment, when testing or developping new modules, to avoid fastidious
  initial configuration.

.. figure:: ../static/description/view_res_users_form.png


**Note**

- You could also be interested by another module named ``base_technical_features``
  in the same OCA repository.

- If you want to always have this feature installed when developping new module
  you could consider use ``module_change_auto_install`` module
  in the OCA / server-tools repository.
