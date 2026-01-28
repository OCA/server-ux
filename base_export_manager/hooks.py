# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Clean up invalid export templates before installing the module.

    This hook identifies and removes export lines that reference non-existent fields.
    This prevents installation errors when migrating from previous versions where
    fields may have been removed or renamed.
    """
    if not env:
        return
    cr = env.cr
    # Get all export templates with their lines
    cr.execute(
        """
        SELECT
            e.id as export_id,
            e.name as export_name,
            e.resource as model,
            el.id as line_id,
            el.name as field_path
        FROM ir_exports e
        INNER JOIN ir_exports_line el ON el.export_id = e.id
        WHERE el.name IS NOT NULL AND el.name != ''
        ORDER BY e.id, el.id
        """
    )
    export_lines = cr.fetchall()

    if not export_lines:
        return

    invalid_lines = []

    for export_id, export_name, model, line_id, field_path in export_lines:
        if not field_path or not model:
            continue

        # Split the field path (e.g., "partner_id/name" -> ["partner_id", "name"])
        field_parts = field_path.split("/")
        current_model = model

        # Check each field in the path
        field_valid = True
        for field_name in field_parts:
            # Check if field exists in current model
            cr.execute(
                """
                SELECT name, ttype, relation
                FROM ir_model_fields
                WHERE model = %s AND name = %s
                LIMIT 1
                """,
                (current_model, field_name),
            )
            field_info = cr.fetchone()

            if not field_info:
                # Field doesn't exist
                field_valid = False
                break

            # If it's a relational field, update current_model for next iteration
            field_type = field_info[1]
            if field_type in ("many2one", "one2many", "many2many"):
                current_model = field_info[2]
                if not current_model:
                    field_valid = False
                    break

        if not field_valid:
            invalid_lines.append(
                {
                    "line_id": line_id,
                    "export_id": export_id,
                    "export_name": export_name,
                    "model": model,
                    "field_path": field_path,
                }
            )

    # Delete invalid lines
    if invalid_lines:
        line_ids = [line["line_id"] for line in invalid_lines]
        cr.execute("DELETE FROM ir_exports_line WHERE id IN %s", (tuple(line_ids),))

        # Log the cleanup
        _logger.warning(
            "Cleaned up %d invalid export template lines before installation",
            len(invalid_lines),
        )

        # Group by export template for detailed logging
        by_export = {}
        for line in invalid_lines:
            exp_id = line["export_id"]
            if exp_id not in by_export:
                by_export[exp_id] = {
                    "name": line["export_name"],
                    "model": line["model"],
                    "fields": [],
                }
            by_export[exp_id]["fields"].append(line["field_path"])

        for exp_id, data in by_export.items():
            _logger.info(
                "Export template '%s' (ID: %d, Model: %s): Removed invalid fields: %s",
                data["name"],
                exp_id,
                data["model"],
                ", ".join(data["fields"]),
            )
