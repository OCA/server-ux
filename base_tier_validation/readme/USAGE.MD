**Bypass tier validation context key**

```skip_validation_check```: This flag will bypass the tier validation
workflow. When this context key is set to True, aall tier validations within the write and _write methods are bypassed.

This is the ideal flag to use in your unit tests.

``` python
# Example: Confirming a sale order in a unit test
# without triggering the tier validation workflow.
sale_order.with_context(skip_validation_check=True).action_confirm()
```

**Skip initial state check**

```skip_check_state_condition```: This forces the initial state check to pass. This makes the system believe the record is in a valid state to begin the validation process, even if it isn't.
