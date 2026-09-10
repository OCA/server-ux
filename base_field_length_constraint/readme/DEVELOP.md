Values built at serialization time - a concatenation, a split, a converted
code - never reach a stored field, so no ORM constraint can see them. Check
them against the rules of the field whose limit applies:

```python
self.env["base.field.length.rule"].check_value(
    "res.partner", "ref", derived_value, record=partner
)
```

The string is measured exactly as given, with no html extraction.

Pass the record whenever there is one. It is what the company of a rule is
resolved against, and a rule carrying a condition is **skipped entirely**
without it, since there is nothing to evaluate the condition on.

`validate_records(records, field_names=None)` does the same for the stored
values of existing records.

Both raise a `ValidationError` by default, and return the list of violations
instead when `raise_on_error=False`. Neither logs nor notifies anyone: they
inspect values, so a warning-enforcement rule is only ever returned to the
caller.
