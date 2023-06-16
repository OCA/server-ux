#. Go to *Settings > Custom Filters*.
#. Create a record assigning model, type (search/filter/groupby) and necessary attributes.
   Available fields and corresponding attributes (in brackets) for each type are as follows:

   Search:

      * Search Field (``name``)
      * Filter Domain (``filter_domain``)
      * User Groups (``groups``)

   Filter:

      * Domain (``domain``)
      * User Groups (``groups``)

   Group By:

      * Group By Field (field to be assigned to ``group_by`` context)
      * User Groups (``groups``)

   See `the official documentation <https://www.odoo.com/documentation/16.0/developer/reference/backend/views.html#search>`_ for the definition of each attribute.
   Additionally, filter and group-by records can be respectively grouped together with "Group" assignment (there will be a separator in between groups).
