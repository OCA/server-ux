This module extends *Base Tier Validation* to keep completed tier reviews as
history instead of deleting them once a validation cycle ends (e.g. on
rejection restart or when the record is reset/cancelled).

Without this module, reviews are removed when the validation cycle is reset, so
there is no trace of who approved or rejected a document in a previous cycle.
With this module, completed reviews (approved/rejected) can be archived and kept
as a *Reviews History*, viewable on the document and from a dedicated menu.
