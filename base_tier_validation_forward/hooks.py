# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def uninstall_hook(env):
    """Revert table tier_review back to original before this module"""
    env.cr.execute(
        "update tier_review a set sequence = "
        "(select floor(sequence) from tier_review b where a.id = b.id);"
    )
    env.cr.execute(
        "update tier_review a set status = 'approved' where status = 'forwarded';"
    )

    columns_to_drop = [
        "name",
        "review_type",
        "reviewer_id",
        "reviewer_group_id",
        "has_comment",
        "approve_sequence",
    ]
    drop_sql = ", ".join([f"DROP COLUMN {col} CASCADE" for col in columns_to_drop])
    env.cr.execute(f"ALTER TABLE tier_review {drop_sql};")
