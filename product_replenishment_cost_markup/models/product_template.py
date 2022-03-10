from openerp import models, fields, api, exceptions

import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = 'product.template'

    markup = fields.Float(
        string='% markup',
    )

    markup_price = fields.Float(
        string='markup price',
        compute='_compute_markup_price',
        store=False,
        compute_sudo=True,
        digits='Product Price',
        help="markup price on the currency of the product",
    )

    @api.onchange('replenishment_cost_rule_id')
    def onchange_replenishment_cost_rule_id(self):
        self.markup = self.replenishment_cost_rule_id.markup

    def update_markup(self):
        for product_id in self:
            product_id.markup = product_id.replenishment_cost_rule_id.markup

    def price_compute(self, price_type, uom=False, currency=False, company=False):
        if price_type == 'markup_price':
            self.sudo()._compute_markup_price()
        prices = super().price_compute(price_type, uom, currency, company)
        return prices

    @api.depends(
        'markup',
        'currency_id',
        'supplier_price',
        'supplier_currency_id',
        'replenishment_cost_type',
        'replenishment_base_cost',
        # beccause field is not stored anymore we only keep currency and
        # rule
        # 'replenishment_base_cost_currency_id',
        # # because of being stored
        #'replenishment_base_cost_currency_id.rate_ids.rate',

        # # and this if we change de date (name field)
        # 'replenishment_base_cost_currency_id.rate_ids.name',
        # rule items
        'replenishment_cost_rule_id.item_ids.sequence',
        'replenishment_cost_rule_id.item_ids.percentage_amount',
        'replenishment_cost_rule_id.item_ids.fixed_amount',
    )
    def _compute_markup_price(self):
        for rec in self:
            # rec.markup_price = 0.0

            if rec.replenishment_cost_type in ['supplier_price', 'last_supplier_price']:
                replenishment_base_cost = rec.net_price
            elif rec.replenishment_cost_type == 'manual':
                replenishment_base_cost = rec.replenishment_cost

            # TODO: Por ahora no uso el markup  del supplierinfo
            rec.update({
                'markup_price': replenishment_base_cost * (rec.markup / 100 + 1)
            })
