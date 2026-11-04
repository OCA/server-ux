It adds a new field `perm_duplicate` (Duplicate Access) to `ir.model.access` to control
whether groups have duplicate rights. In the frontend, the module post-processes views
to dynamically inject `duplicate="0"` on form and list views when a user lacks duplication
rights, hiding the duplicate button.
