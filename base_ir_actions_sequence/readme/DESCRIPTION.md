This module allows to assign sequence to every action (``ir.actions.actions``),
and therefore any model that inherits from it (like ``ir.actions.report``,
``ir.actions.server``, ``ir.actions.act_window``...) can be ordered by sequence.

This is useful when you want to control the order of actions displayed in
various parts of the Odoo interface, such as the order of reports in the print
menu, or the order of server actions in the action menu.
