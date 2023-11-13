This module makes importing data from CSV and Excel files optional for each user,
depending on whether `Import CSV/Excel files` is ticked on the `Access Rights`
tab on the user form. This corresponds to a user group by the same name.
Only users that belong to this group will have the `Import records` button
available under the `Favorites` button of each list or kanban view.

If this GUI restriction is circumvented (through a crafted JSONRPC call for
instance), there is another check in the backend to prevent batch imports by
restricted users.
