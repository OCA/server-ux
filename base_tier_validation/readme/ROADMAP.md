This is the list of known issues for this module. Any proposal for
improvement will be very valuable.

- **Issue:**

  When using approve_sequence option in any tier.definition there can be
  inconsistencies in the systray notifications.

  **Description:**

  Field can_review in tier.review is used to filter out, in the systray
  notifications, the reviews a user can approve. This can_review field
  is updated **in the database** in method review_user_count, this can
  make it very inconsistent for databases with a lot of users and
  recurring updates that can change the expected behavior.

- **Default _tier_validation_manual_config parameter**

  The parameter \_tier_validation_manual_config will become False, on
  18.0, the default value is True, as the change is applied after the
  migration. In order to use the new behavior we need to modify the
  value on our expected model.

- **Extraneous functions**
  All functions:

  _get_to_validate_message_name

  _get_to_validate_message

  _get_validated_message

  _get_rejected_message

  are related to message building should be moved into their own module. This module is
    already heavy enough as it is

- **Obsolete fields:**

  The fields "rejected" and "validated" are kept for compatibility reasons and should be
  removed in 19.0

- **Usability and architecture**

  Implement the good feedback listed here about usability
  https://github.com/OCA/server-ux/pull/1097#pullrequestreview-2961078706

- **More cleanup**

  There are too many computes on tier reviews as evidenced by the remaining invalidate_* function calls in tests.
  It would be simpler to manage if these functions were in their own standalone function
