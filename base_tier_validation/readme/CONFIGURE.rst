To configure Tier Validations, you need to:

#. Go to *Settings > Technical > Tier Validations > Tier Definition*.
#. Create as many tiers as you want for any model having tier validation
   functionality.

**Note:**

* If check *Notify Reviewers on Creation*, all possible reviewers will be notified by email when this definition is triggered.
* If check *Comment*, reviewers can comment after click Validate or Reject.
* If check *Approve by sequence*, reviewers is forced to review by specified sequence.


To configure Tier Validation Exceptions, you need to:

#. Go to *Settings > Technical > Tier Validations > Tier Validation Exceptions*.
#. Create as many tiers validation exceptions as you want for any model
   having tier validation functionality.
#. Add desired fields to be checked in *Fields*.
#. Add desired groups that can use this Exception in *Groups*.
#. You must check *Write under Validation*, *Write after Validation* or both.

**Note:**

* If you don't create any exception, the Validated record will be readonly and cannot be modified.
* If check *Write under Validation*, records will be able to be modified only in the defined fields when the Validation process is ongoing.
* If check *Write after Validation*, records will be able to be modified only in the defined fields when the Validation process is finished.
* If check *Write after Validation* and *Write under Validation*, records will be able to be modified defined fields always.
