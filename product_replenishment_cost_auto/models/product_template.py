from openerp import models, fields, api, exceptions

import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = 'product.template'

    @api.onchange('categ_id', 'seller_ids', 'replenishment_cost_type')
    def set_replenishment_cost_rule_id(self):
        leaf = []
        if len(self.categ_id) and self.categ_id.parent_path:
            categ_id = [int(x)
                        for x in self.categ_id.parent_path.split('/')[:-1]]
            leaf.append(('categ_id', 'in', categ_id))
        if len(self.seller_ids):
            if self.replenishment_cost_type == 'manual':
                leaf += ['|',
                         ('supplier_id', 'in', self.seller_ids.mapped('name').ids),
                         ('supplier_id', '=', False),
                         ]
            elif self.replenishment_cost_type == 'supplier_price':
                leaf += ['|',
                         ('supplier_id', '=', self.seller_ids[0].name.id),
                         ('supplier_id', '=', False),
                         ]

            elif self.replenishment_cost_type == 'last_supplier_price':
                seller_id = self.seller_ids.sorted(
                    key='last_date_price_updated', reverse=True)[0]

                leaf += ['|',
                         ('supplier_id', '=', seller_id.name.id),
                         ('supplier_id', '=', False),
                         ]
        else:
            leaf.append(('supplier_id', '=', False))

        cost_rule = self.env['product.replenishment_cost.rule'].search(
            leaf, limit=1, order='sequence asc')
        if len(cost_rule):
            if self.replenishment_cost_type == 'manual':
                self.replenishment_cost_rule_id = cost_rule.id
