# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def uninstall_hook(cr, registry):
    """ Revert table tier_review back to original before this module """
    cr.execute(
        "update tier_review a set sequence = "
        "(select floor(sequence) from tier_review b where a.id = b.id);"
    )
    cr.execute(
        "update tier_review a set status = 'approved' where status = 'forwarded';"
    )
