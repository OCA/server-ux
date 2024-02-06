This module adds a new boolean on Record rules that changes
the way they are evaluated.

If a Record Rule is of type "override", then it must pass
in order for the record to be visible.

In other words, "override" record rules are in AND with other
rules, not in OR as they normally are.

Use with caution!
