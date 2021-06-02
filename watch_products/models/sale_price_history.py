from odoo import fields, models


class ProduceSalePriceHistory(models.Model):
    """
    Keep track of the ``product.template`` sale prices as they are changed.
    """

    _name = 'product.sale.price.history'
    _rec_name = 'datetime'
    _order = 'datetime desc'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        ondelete='cascade',
    )
    datetime = fields.Datetime(
        string='datetime',
        default=fields.Datetime.now()
    )
    list_price = fields.Float(
        string='list_price',
    )
