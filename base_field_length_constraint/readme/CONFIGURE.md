Go to *Settings > Technical > Database Structure > Field Length Rules* and
create a rule.

- **Name**: shown in the error message. Use it to identify where the limit
  comes from, so that a violation points at the document to consult.
- **Model** and **Field**: the field to measure. `char`, `text` and `html`
  fields can be selected. An `html` field is measured on the text it renders
  to, not on its markup.
- **Maximum Length** and **Measure**: the limit, counted in characters or in
  bytes. Measure in bytes whenever the receiving side counts bytes - a
  fixed-width record layout, a column with byte semantics - and set the
  **Encoding** to the one that side uses, such as `cp932`. The two only differ
  once the value stops being pure ASCII, so a character limit can pass every
  test and still overflow in production.
- **Condition**: an optional domain. The rule only applies to the records that
  match it. The value is measured again when a record moves into the scope of
  the rule, so turning a partner into a company checks the reference it was
  allowed to keep while it was a person.
- **Company**: if set, the rule only applies to the records of that company and
  of its branches. A record that carries no company of its own is evaluated
  against the active company.
- **Enforcement**: `Error` refuses the save. `Warning` lets it through and
  reports it instead, with a dialog as the value is entered.
- **Custom Message**: replaces the default error message when set.

Several rules may target the same field, so the tightest limit is the
effective one. A value that overruns more than one of them is reported against
each, so that the message always names every rule left to satisfy.

## Rolling out on live data

A rule only checks what is written after it exists, so a record that already
breaches it stays as it is and reports nothing. Create the rule, press **Check
Existing Records**, and correct the values it lists.

The button scans the whole table, which is worth knowing before pressing it on
a model holding millions of rows, and it reports the first 1000 violations. Its
title says so when the list is cut short: correct those, press it again, and
repeat until it comes back clean.
