from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)



class ProductReplenishmentCostRule(models.Model):

    _inherit = 'product.replenishment_cost.rule'
    _order = 'sequence asc'

    supplier_id = fields.Many2one(
        'res.partner',
        string='supplier',
        domain=[('supplier_rank', '>', 0), ]
    )
    categ_id = fields.Many2one(
        'product.category',
        string='Category',
    )
    sequence = fields.Integer(
        string='sequence',
        compute="_compute_sequence",
        readonly=True,
        store=True,

    )
    discount_total = fields.Float(
        string='discount total',
        compute='_compute_total_discount',
        store=True
    )

    @api.depends('item_ids')
    def _compute_total_discount(self):
        for rule in self:
            cost = 100
            for line in rule.item_ids:
                value = cost * (line.percentage_amount / 100.0) 
                if line.add_to_cost:
                    cost = cost + value

            rule.discount_total = 100 - cost    

    def action_implement_rule(self):
        force = self.env.context.get('force_assign', False)
        for rule in self:
            leaf = [('categ_id', 'child_of', rule.categ_id.id),
                    ]
            if not force:
                leaf.append(('replenishment_cost_rule_id', '=', False))

            if len(rule.supplier_id):
                leaf.append(('seller_ids.name', '=', rule.supplier_id.id))
            product_ids = self.env['product.template'].search(leaf)
            manual_product_ids = product_ids.filtered(
                lambda x: x.replenishment_cost_type == 'manual')
            if manual_product_ids:
                manual_product_ids.replenishment_cost_rule_id = rule.id
            no_manual_product_ids = product_ids - manual_product_ids
            if no_manual_product_ids:
                if len(rule.supplier_id):
                    supplier_id_info = no_manual_product_ids.mapped(
                        'seller_ids').filtered(lambda s: s.name.id == rule.supplier_id.id)
                else:
                    supplier_id_info = no_manual_product_ids.mapped('seller_ids')
                supplier_id_info.replenishment_cost_rule_id = rule.id
        self.recompute_prices()

    def recompute_prices(self):
        self.product_ids._compute_replenishment_cost()
        return True


    @api.depends('categ_id')
    def _compute_sequence(self):
        for rule in self:
            max_value = 20
            if rule.categ_id.parent_path:
                rule.sequence = (
                    max_value - len(rule.categ_id.parent_path.split('/'))) * 100
            else:
                rule.sequence = 2000

    @api.onchange('supplier_id', 'categ_id')
    def change_name(self):
        for rule in self:
            if len(rule.supplier_id):
                categ_name = self.categ_id.name if len(
                    self.categ_id) else _('All')
                rule.name = "%s %s" % (rule.supplier_id.name, categ_name)
