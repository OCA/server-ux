from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if openupgrade.table_exists(cr, "date_range_res_company_rel"):
        openupgrade.logged_query(
            cr,
            """
            UPDATE date_range dr
            SET company_id = drrcr.res_company_id
            FROM date_range_res_company_rel drrcr,
                date_range_type drt
            WHERE
                dr.id = drrcr.date_range_id
                AND drt.id = dr.type_id
                AND (drt.company_id IS NULL OR drt.company_id = drrcr.res_company_id)
            """,
        )
        openupgrade.logged_query(
            cr,
            """SELECT
                drrcr.res_company_id,
                dr.id
            FROM date_range dr
            JOIN date_range_res_company_rel drrcr ON dr.id = drrcr.date_range_id
            WHERE dr.company_id != drrcr.res_company_id
            """,
        )
        for company_id, date_range_id in cr.fetchall():
            date_range = env["date.range"].browse(date_range_id)
            date_range_type = date_range.type_id
            if (
                date_range_type.company_id
                and date_range_type.company_id.id != company_id
            ):
                date_range_type = date_range.type_id.copy({"company_id": company_id})
            date_range.copy({"company_id": company_id, "type_id": date_range_type.id})
    rule = env.ref("date_range.date_range_comp_rule")
    if rule:
        rule.domain_force = (
            "['|',('company_id', 'in', company_ids),('company_id','=',False)]"
        )
