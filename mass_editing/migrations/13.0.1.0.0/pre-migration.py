# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    if not version:
        return
    # Don't execute if already migrated in v12
    cr.execute("SELECT 1 FROM pg_class WHERE relname = %s", ("mass_editing",))
    if cr.fetchone():
        return
    # First remove the obsolete constraint created by the existence of the
    # remove M2M field 'field_ids' between mass.object and ir.model.fields
    cr.execute(
        """
        DELETE FROM ir_model_relation
        WHERE name = 'mass_field_rel';
        """
    )
    # Rename table for consistency reason
    cr.execute(
        """
        ALTER TABLE mass_object
        RENAME TO mass_editing;
    """
    )
    # Create and Compute new required field
    cr.execute(
        """
        ALTER TABLE mass_editing
        ADD COLUMN action_name varchar;
    """
    )
    cr.execute(
        """
        UPDATE mass_editing
        SET action_name = name;
    """
    )
    cr.execute(
        """
        alter sequence mass_object_id_seq rename to mass_editing_id_seq;"""
    )
