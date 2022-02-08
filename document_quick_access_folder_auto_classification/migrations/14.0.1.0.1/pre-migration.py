# Copyright 2020 Creu Blanca

from openupgradelib import openupgrade

fields_to_unstore_safely = [
    "document_quick_access_folder_auto_classification."
    "field_document_quick_access_missing__state",
]


@openupgrade.migrate()
def migrate(env, version):
    for field_key in fields_to_unstore_safely:
        field = env.ref(field_key, raise_if_not_found=False)
        if field:
            openupgrade.logged_query(
                env.cr, "UPDATE ir_model_fields SET store=false WHERE id=%s" % field.id
            )
    openupgrade.logged_query(
        env.cr,
        """
            DELETE FROM ir_model_relation imr
            USING ir_model im
            WHERE imr.model = im.id AND im.model IN (
                'document.quick.access.missing'
            )""",
    )
