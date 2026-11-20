This module enforces a maximum length on `char`, `text` and `html` fields,
defined as configuration data rather than in code.

A rule declares the limit of one field of one model, counted in characters or
in the bytes of a given encoding, and optionally restricted to a company or to
the records matching a domain. An over-long value is refused when the record
is saved, or only reported if the rule is set to warn.
