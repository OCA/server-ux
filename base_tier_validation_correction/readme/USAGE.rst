To create/edit Tier Review Correction

* Login as user with Tier Review Correction role
* Go to menu Settings > Technical > Tier Validation > Tier Review Correction
* Create a new tier correction, by selecting,

  * Correction Type, in this case, Reassign Reviewer(s)
  * Document Model, i.e., Purchase order
* Find documents with pending reviews by,

  * Reviewer(s)
  * Name Search
* Then set default value to change, in this case,

  * New Reviewer(s)
* Click button "Prepare", if any document matched, it should list in Correction Detail table.
* For each correction line, user can still change the affected tier reviews, and new reviewers.
* Click button "Make Correction" to finalize the operation.
* As an option, click on "Revert Back" to set back to original status.

  * For case Reassign Reviewer(s), system to get the original reviewers from tier definition as set it back.

Quick access, from a working document, to create/view Tier Review Correction

* As user with Tier Review Correction role
* On any document, i.e., Purchase Order, with validation already started.
* On the yellow banner (pending state), click on "Change Reviewer" link on its right side.

  * If this document has no Correction yet, it will create new.
  * If the document already has some Corrections, it will show those corrections.

To run the Tier Review Correction by scheduled job

* As user with Tier Review Correction role
* On any Tier Review Correction, open tab "Scheduled Action"
* Setup the datetime to Scheduled Correct and Scheduled Revert. By default,
  scheduled action "Tier Correction Scheduler" will run every 1 hour.
