To create configuration wizard:

Use confirm wizard which return method (return_type = method):

.. code-block:: python

  def change_address(self, address):
    if not self._context("skip_confirm", False):
      # Confirmation wizard
      return (
        self.env["confirmation.wizard"]
        .with_context(skip_confirm=True)
        .confirm_message(
          _("Do you want to change the partner's address?"),
          records=self.env["res.partner"].browse(1), # One or more records
          title="Confirm",
          method="change_address",
          callback_params={"address": address}
        )
      )
    ... # Your code here

Use confirm wizard which does nothing and closes itself when clicking confirm (return_type = window_close):

.. code-block:: python

  def method(self):
    ...
    return (
      self.env["confirmation.wizard"]
      .with_context(hide_cancel=True)
      .confirm_no_action_message(
        message="Message",
        title="Notification"
      )
    )
