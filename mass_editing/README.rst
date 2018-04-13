.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============
Mass Editing
============

This module provides the following features:

* You can add, update or remove the values of more than one records on the fly at the same time.

* You can configure mass editing for any Odoo model.

Installation
============

No external library is used.

Configuration
=============

To configure this module, you need to:

* Go to *Settings / Mass Editing / Mass Editing* and configure the object and fields for Mass Editing.

Usage
=====

This module allows to add, update or remove the values of more than one records on the fly at the same time.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/250/11.0

As shown in figure you have to configure the object and fields for mass editing.

* Select the object and add the fields of that object on which you want to apply mass editing.

.. image:: /mass_editing/static/description/mass_editing-1.png
   :width: 70%

* *Add Action*: As shown in figure click on *Add Sidebar Button* to add mass editing option in *Action* option in action.

.. image:: /mass_editing/static/description/mass_editing-2.png
   :width: 70%

* *Go for Mass Editing*: As shown in figure, select the records which you want to modify and click on *Action* to open mass editing popup.

.. image:: /mass_editing/static/description/mass_editing-3.png
   :width: 70%

* Select *Set / Remove* action and write down the value to set or remove the value for the given field.

.. image:: /mass_editing/static/description/mass_editing-4.png
   :width: 70%

* This way you can set / remove the values of the fields.

.. image:: /mass_editing/static/description/mass_editing-5.png
   :width: 70%

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-ux/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Oihane Crucelaegui <oihanecrucelaegi@gmail.com>
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>
* Jay Vora <jay.vora@serpentcs.com>
* Jairo Llopis <jairo.llopis@tecnativa.com>
* Juan Negrete <jnegrete@casasalce.com>

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
