Technical module providing `line.numbering.mixin`, a mixin that numbers the
lines of a record (e.g. the lines of an order) with a position spaced by 10
(10, 20, 30, ...), following the lines' order.

It has no functional effect on its own. It is a building block for modules
that need a stable line reference, shown to users and exchanged with third
parties (e.g. a position on purchase, sale or stock move lines).

Positions are renumbered automatically when lines are added or removed, in any
state of the record. Consuming modules can opt out for specific records (e.g.
records already sent to a partner).
