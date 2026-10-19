Once a rule is active it works on its own, with no code to call. Each
enforcement reports itself once:

- An `Error` rule refuses the save, with one validation error listing every
  violation of that write.
- A `Warning` rule shows a dialog as soon as the value is entered, then lets
  the save through, notifies the user and writes a line to the log.

The **Check Existing Records** button on the rule form lists the stored
records that already violate it. This is how the records predating a rule are
found, since a field is only revalidated when it is written, or when the
record moves into the scope of the rule.
