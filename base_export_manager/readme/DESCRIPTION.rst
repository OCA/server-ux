This module extends the export capability:

1. It allows an admin to manage export profiles (``ir.exports``) that
   Odoo stores internally but does not show anywhere.
2. It also adds a new column to access rights to enable/disable export and
   override the export method to check if the user is allowed to export. Export
   is enabled by default.
