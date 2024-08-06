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
    env.cr.execute("alter table tier_review drop column name cascade;")
    env.cr.execute("alter table tier_review drop column review_type cascade;")
    env.cr.execute("alter table tier_review drop column reviewer_id cascade;")
    env.cr.execute("alter table tier_review drop column reviewer_group_id cascade;")
    env.cr.execute("alter table tier_review drop column has_comment cascade;")
    env.cr.execute("alter table tier_review drop column approve_sequence cascade;")
