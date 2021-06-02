from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    second_price = fields.Float(
        'Second Price', compute='_compute_second_price',
        digits='Product Price'
    )

    """modelo_articulo = fields.Char(
        string='Filed Label',
    )"""

    def _add_price_history(self):
        ''' Store the standard price change in order to be able to retrieve the list_price of a product template for a given date'''
        vals_list = []
        for product in self:
            vals_list.append({
                'product_tmpl_id': product.id,
                'list_price': product.list_price,
            })
        self.env['product.sale.price.history'].create(vals_list)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProductTemplate, self).create(vals_list)
        records._add_price_history()
        return records

    def write(self, vals):
        records = super(ProductTemplate, self).write(vals)
        if 'list_price' in vals:
            self._add_price_history()
        return records

    def _compute_second_price(self):
        prices = self._compute_second_price_no_inverse()
        for template in self:
            template.second_price = prices.get(template.id, 0.0)

    def _compute_second_price_no_inverse(self):
        """The _compute_template_price writes the 'list_price' field with an inverse method
        This method allows computing the price without writing the 'list_price'
        """
        prices = {}
        pricelist_id = self.env['ir.config_parameter'].sudo().get_param("watch.productpricelist", '1')
        pricelist = self.env['product.pricelist'].browse(int(pricelist_id))
        partner = self.env.context.get('partner')
        quantity = self.env.context.get('quantity', 1.0)

        if pricelist:
            quantities = [quantity] * len(self)
            partners = [partner] * len(self)
            prices = pricelist.get_products_price(
                self, quantities, partners)

        return prices
