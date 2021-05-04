#. Activate the developer mode.
#. Go to Settings > Technical > Sequences & Identifiers > Sequences.
#. Click on sequence to edit.
#. Add value in Number Of Year (positive/negative).

**Example**

* Number Of Year = 543 (This year 2020 A.D.)
* Prefix = BILL/%(range_year)s/

Normally, Sequence will generate BILL/2020/0001.
When you add Number Of Year = 543, Sequence will generate BILL/2563/0001.
