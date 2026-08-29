Keeping tier review history is resolved from two configuration levels:

#. **Company** → *Settings > Tier Validation > Keep Tier Review History*
   (boolean). Sets the default for all tier definitions of the company. In
   multi-company, switch to the relevant company before changing it.
#. **Tier Definition** → *Keep Tier Review History* (selection: *Keep* / *Do
   Not Keep* / empty), on the *More Options* tab of the tier definition
   (*Settings > Technical > Tier Validations > Tier Definitions*). Leave empty
   to inherit the company default. *Keep* or *Do Not Keep* overrides the company
   default for this tier definition.

When keeping is effective for a tier definition, its completed
(approved/rejected) reviews are archived as history instead of being deleted
when the validation cycle ends. The archived reviews are shown in the *Reviews
History* section of the document and can be browsed from
*Settings > Technical > Tier Validations > Tier Reviews*.

The *Reviews History* section is injected automatically only into documents
whose tier validation view is built automatically
(``_tier_validation_manual_config = False``), which is the case of the usual
consumers (purchase, sale, account move). A model that configures its tier
validation view manually must add ``<field name="review_history_ids" />`` to
its form view to display the history.
