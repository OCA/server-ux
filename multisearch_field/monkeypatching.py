# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo.models import BaseModel
from odoo.osv import expression

_where_calc_orginal = BaseModel._where_calc


def _where_calc(self, domain, active_test=True):
    """Override of the Python method to remove the dependency of the unit
    fields"""
    if self.check_access_rights("read") and self != self.env["ir.config_parameter"]:
        list_separator = (
            self.env["ir.config_parameter"].sudo().get_param("multi_search_separator")
        )
    else:
        list_separator = False
    if not list_separator or not domain:
        return _where_calc_orginal(self, domain, active_test)

    domain_list = []
    domain_value = []
    domain_list_value = []
    nlist_sep = []
    for sep in list_separator:
        nlist_sep.append(sep)
    for dom in domain:
        if (
            len(dom) == 3
            and isinstance(dom[2], str)
            and dom[2].startswith("/")
            and any(separator in dom[2] for separator in list_separator)
        ):
            text_search = dom[2].replace("/", "", 1)
            value_list = re.split("{}".format(nlist_sep), text_search)
            value_list.append(text_search)
            value_list.append(dom[2])
            value_list_set = set(value_list)
            for separator in list_separator:
                value_list_set = value_list_set.union(text_search.split(separator))
            for value in value_list_set:
                domain_search_field = [(dom[0], dom[1], value)]
                domain_value.append(domain_search_field)
            domain_list_value = expression.OR(domain_value)
            for item in domain_list_value:
                domain_list.append(item)
            domain_value = []
            domain_list_value = []
        else:
            domain_list.append(dom)
    res = _where_calc_orginal(self, domain_list, active_test)
    return res


BaseModel._where_calc = _where_calc
