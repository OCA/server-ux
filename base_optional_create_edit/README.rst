.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Base Optional Create Edit
=========================

Add the possibility to remove create and create/edit from many2one fields, for a specific model

This module allows to avoid to *create*/ *create/edit* new records, through many2one
fields, for a specific model.
You can configure which models should allow *create*/ *create/edit*.
When specified, the *create*/ *create/edit* option will always open the standard create
form.

This module is based on the behavior for quick_create (base_optional_quick_create)

Usage
=====

To use this module, you need to:

 * go into the menu of *ir_model*,
 * select the model for which you want to disable the quick create option,
 * enable the option *Avoid create/edit*.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lindsay Marion <lindsay.marion@acsone.eu>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
