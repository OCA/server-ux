## Setup

- Go to Settings > Technical > Sequences & Identifiers > Sequences and open the
  sequence you want to reset.
- Tick **Use subsequences per date_range**. The **Range Reset** field stays
  hidden until you do.
- Set **Range Reset** to Daily, Weekly, Monthly or Yearly.

## An existing subsequence keeps the setting dormant

Odoo only builds a new subsequence when no existing one covers the current
date. Setting Range Reset leaves the subsequences already on the record alone,
so a sequence that still carries a 1 January to 31 December row keeps drawing
from that row and the numbering never resets.

If nothing happens after setting Range Reset, open the **Subsequences** tab and
look at the rows. Shorten the **To** date on the row covering today, or delete
it, and the next number drawn builds a fresh range on the new period. Editing
rather than deleting keeps the earlier numbering on record.

## Range boundaries

| Range Reset | From | To |
| --- | --- | --- |
| Daily | the current date | the current date |
| Weekly | Monday of the current week | the following Sunday |
| Monthly | the 1st of the current month | the last day of that month |
| Yearly | 1 January | 31 December |

The computed range is then trimmed against neighbouring subsequences so that
ranges never overlap. If an existing row ends between the computed start and
today, the new range starts the day after it. If an existing row starts between
today and the computed end, the new range ends the day before it. The first
range after switching can therefore be shorter than a full period.
