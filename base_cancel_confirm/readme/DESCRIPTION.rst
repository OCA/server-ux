Many document model that already has cancel action may also want a confirm dialog with option to provide reason.

This module does not provide a functionality by itself but an abstract model
to easily implement a confirm with reason wizard when cancel button is clicked.
If reason is provided, it will be visible in form view.

**Note:** To be able to use this module in a new model you will need some
development.

You can see implementation example as followings,

* `sale_cancel_confirm <https://github.com/OCA/sale-workflow>`_
* `purchase_cancel_confirm <https://github.com/OCA/purchase-workflow>`_
* `purchase_request_cancel_confirm <https://github.com/OCA/purchase-workflow>`_
* `account_move_cancel_confirm <https://github.com/OCA/account-invoicing>`_
