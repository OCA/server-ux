# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        model_domain = []
        if not self.env.context.get('mass_edit', False):
            model_domain = args
        else:
            for domain in args:
                if (len(domain) > 2 and domain[0] == 'model_id' and
                        isinstance(domain[2], str) and
                        list(domain[2][1:-1])):
                    model_ids = list(map(int, domain[2][1:-1].split(',')))
                    model_domain += [('model_id', 'in', model_ids)]
                else:
                    model_domain.append(domain)
        return super(IrModelFields, self).search(args=model_domain,
                                                 offset=offset,
                                                 limit=limit, order=order,
                                                 count=count)
