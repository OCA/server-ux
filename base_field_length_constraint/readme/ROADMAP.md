- A rule on a translated field is checked in the language of the user
  performing the write. Its other translations are not checked.
- A rule scoped to a company judges a record that carries no company of its
  own by the active company of whoever writes it, so the same value can be
  refused for one user and accepted for another, and a cron or a `sudo()`
  write is judged by the superuser's company.
- The notification of a warning enforcement is addressed to the user the write
  runs as, so a write made by a cron, a server action or a `sudo()` call
  notifies the superuser and nobody sees it. The log entry remains.
