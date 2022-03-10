from odoo import models, fields, api, _


class ProductReplenishmentCostRule(models.Model):

    _inherit = 'product.replenishment_cost.rule'

    markup = fields.Float(
        string='markup',
    )

    def action_update_markup(self):
        self.product_ids.markup = self.markup

    def recompute_prices(self):
        super().recompute_prices()
        self.product_ids.markup = self.markup
        self.product_ids._compute_markup_price()
        return True