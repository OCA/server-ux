The web client displays 40 lines in the one2many / many2many lists of a form
(e.g. the journal items of an entry) before paging.

This module sets this number for all these lists, with the system parameter
`x2many_limit.limit` (200 by default). A list with its own `limit` attribute
keeps it.
