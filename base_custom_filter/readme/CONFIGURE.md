1.  Go to *Settings \> Custom Filters*.

2.  Create a record assigning model, type (search/filter/groupby) and
    necessary attributes. Available fields and corresponding attributes
    (in brackets) for each type are as follows:

    Search:

    > - Search Field (`name`)
    > - Filter Domain (`filter_domain`)
    > - User Groups (`groups`)

    Filter:

    > - Domain (`domain`) - OR -
    > - Date Field (`date_field`) - creates a date filter with period options
    > - User Groups (`groups`)
    >
    > **Note:** For filter type, you must specify either Domain or Date Field,
    > but not both. Date filters automatically provide period options like
    > Today, This Week, This Month, This Quarter, and This Year.

    Group By:

    > - Group By Field (field to be assigned to `group_by` context)
    > - User Groups (`groups`)

    See [the official
    documentation](https://www.odoo.com/documentation/16.0/developer/reference/backend/views.html#search)
    for the definition of each attribute. Additionally, filter and
    group-by records can be respectively grouped together with "Group"
    assignment (there will be a separator in between groups).

3.  Filter groups (accessible via *Settings \> Custom Filters \> Custom
    Filter Groups*) support the following optional settings:

    - Insert XPath: XPath expression for the insertion point
      (e.g. `//filter[@name='my_filter']`)
    - Insert Position: Insert before or after the target element
    - Separator Position: Place separator before, after, or none
      (filter type only)
