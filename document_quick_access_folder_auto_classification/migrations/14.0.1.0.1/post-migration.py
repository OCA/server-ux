# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade  # pylint: disable=W7936

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.table_exists(env.cr, "document_quick_access_missing"):
        return
    integration_field_name = openupgrade.get_legacy_name(
        "document_quick_access_missing_id"
    )
    if not openupgrade.column_exists(
        env.cr, "edi_exchange_record", integration_field_name
    ):
        openupgrade.logged_query(
            env.cr,
            """
                    ALTER TABLE edi_exchange_record
                    ADD COLUMN %s numeric"""
            % integration_field_name,
        )
    backend = env.ref("document_quick_access_folder_auto_classification.edi_backend")
    exchange_type = env.ref(
        "document_quick_access_folder_auto_classification.exchange_type"
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO edi_exchange_record (
            identifier, type_id, backend_id, model, res_id, exchanged_on,
            edi_exchange_state,
            exchange_filename,
            create_date, create_uid, write_date, write_uid,
            {integration_field}
        )
        SELECT
            CONCAT('MIG_DOCUMENT_QUICK_ACCESS_FOLDER_', dqam.id),
            {exchange_type},
            {backend},
            dqam.model,
            dqam.res_id,
            dqam.create_date,
            case when dqam.state = 'pending' then 'input_processed_error'
                else 'input_processed'
            end,
            ia.name,
            dqam.create_date, dqam.create_uid, dqam.write_date, dqam.write_uid, dqam.id
        FROM document_quick_access_missing as dqam
            LEFT JOIN ir_attachment ia ON ia.id = dqam.attachment_id
        """.format(
            integration_field=integration_field_name,
            exchange_type=exchange_type.id,
            backend=backend.id,
        ),
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment at
        SET res_model = 'edi.exchange.record', res_id = eer.id,
            res_field = 'exchange_file'
        FROM document_quick_access_missing dqam
            INNER JOIN edi_exchange_record eer on eer.{integration_field} = dqam.id
        WHERE dqam.attachment_id = at.id
        """.format(
            integration_field=integration_field_name,
        ),
    )
