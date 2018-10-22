from odoo import models, api


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def _message_track(self, tracked_fields, initial):
        """For a given record, fields to check (column name, column info)
        and initial values, return a structure that is a tuple containing :

        - a set of updated column names
        - a list of changes (old value, new value, column name, column info)
        """
        changes = super(MailThread, self)._message_track(
            tracked_fields, initial)[0]
        tracking_value_ids = []
        track_obj = self.env['mail.tracking.value']

        for col_name, col_info in tracked_fields.items():
            initial_value = initial[col_name]
            new_value = getattr(self, col_name)

            if new_value != initial_value and (new_value or initial_value):
                track_sequence = getattr(
                    self._fields[col_name], 'track_sequence', 100)
                tracking = track_obj.create_tracking_values(
                    initial_value, new_value, col_name,
                    col_info, track_sequence)
                if tracking:
                    tracking_value_ids.append([0, 0, tracking])

        return changes, tracking_value_ids
