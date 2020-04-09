#. Go to *Settings > Technical > User Interface > Custom Field Filters*.
#. Create a new record, and define following information:

   * The **Model** for which you are defining the filter. It will appear in all
     the search views of this model.
   * The label you want to see on the search line on the **Name** field. This
     field allows translations for proper UI in different languages.
   * The **Expression**, which is the field chain string with dot notation.
     Examples: `product_id`, `product_id.seller_ids.name`, `partner_id.lang`.
   * Optionally, you can fill **Position After** for indicating after which
     existing field (technical name) the filter will appear. If empty or not
     found, the filter will be added at the end.
#. You can reorder records for determining sorting for multiple filters for the
   same model with the arrow handle in the left part.
