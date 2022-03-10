from odoo import fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(
        selection_add=[
            ('markup_price', 'Markup price'),
            ('replenishment_base_cost_on_currency', 'purchase cost'),
            ('replenishment_cost', 'PruchaseNET cost'),
        ]
    )
