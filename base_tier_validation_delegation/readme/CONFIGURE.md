To configure Tier Validations Delegation, you need to:

1.  Go to **Settings \> Users & Companies \> Users** and select their
    own user profile (or click their name in the top right corner and
    select **My Profile**).
2.  Navigate to the **Delegation** tab.
3.  Check the **On Holiday** box.
4.  Optionally, set the **Holiday Start/End Dates**. If no dates are
    set, the delegation is considered active as long as the "On Holiday"
    box is checked.
5.  Select a **Default Replacer**. This is the user who will receive all
    validation requests.

The module includes two daily automated jobs:

- Holiday Status Update: This job automatically checks the "On Holiday"
  box for any user whose Holiday Start Date is today. This activation
  triggers the same logic as a manual change, meaning all of their
  existing pending reviews are automatically reassigned to their
  replacer. It also unchecks the box for users whose Holiday End Date
  has passed.
- Delegation Reminder: This job sends a reminder notification to users 3
  days before their scheduled holiday if they have not yet configured a
  replacer.
