Once configured, the module automatically controls the visibility of the Archive and Unarchive actions across the system:

* In Form views, the `Active` stat button will be hidden if the user lacks the required permission to toggle it (e.g., if a record is active and the user lacks archive permission, the button is hidden).
* In List and Kanban views, the `Archive` and `Unarchive` action menu items will be hidden depending on the user's permissions.
