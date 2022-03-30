To configure this module, you need to:

#. Go to *Settings > Technical > Tier Validations > Tier Definition*.
#. Create as many tiers as you want for any model having tier validation
   functionality.

**Note:**

* If check *Notify Reviewers on Creation*, all possible reviewers will be notified by email when this definition is triggered.
* If check *Comment*, reviewers can comment after click Validate or Reject.
* If check *Approve by sequence*, reviewers is forced to review by specified sequence.
* If you want to introduce a workflow where there are multiple sequential
  tiers of validations, instead of all validations being triggered at once,
  use the field *validation_max_sequence* in your definition. This field is
  available in all models that support the tier validation. For example,
  trigger the validation of the Supply Chain Manager (tier definition with
  sequence 20) only when the Supply Chain User has approved (tier definition
  with sequence 10). In this case you would set your Tier Definition for
  Supply Chain Manager to be applied when *validation_max_sequence = 10*.
