This module add an advance option to base_tier_validation.

* To allow "Forward" the tier to different user.

**Sample use case:**

A user is appointed to approve a tire, but he/she don't want to make decision
for some reason, and want to pass/forward the decision to another person.

User can then click on Forward instead of Approve. A new tier with minor sequence will be
created on the reviewer table, and new user will be able to make approval decision.

**Note:** To enable Forward button in the desired view, you will need some development.

See `purchase_tier_validation_forward <https://github.com/OCA/purchase-workflow>`_ as an example of implementation.
