To use this module, make sure that the template you are going to write the message inherits from `mail.thread`.

You can call the template like this:

```python
def custom_function(self):
    """Adds a chatter message to origin and destiny records"""
    for record in self:
        destiny_records = record._create_destiny_records()  # A bunch of Destiny Records
        mt_note_subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')

        # Add note to chatter that indicates destiny records
        record.message_post_with_view(
            'mail_message_destiny_link_template.message_destiny_link',
            values={'self': record, 'destiny': destiny_records, "edit": False or True},
            subtype_id=mt_note_subtype_id,
        )

        # Origin Link common usage to show differences
        for destiny_record in destiny_records:
            destiny_record.message_post_with_view(
                'mail.message_origin_link',
                values={'self': destiny_record, 'origin': record, "edit": False or True},
                subtype_id=mt_note_subtype_id,
            )
```
