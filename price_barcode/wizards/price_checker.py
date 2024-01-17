##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _


class priceChecker(models.TransientModel):

    _name = 'price.checker'
    _inherit = ['barcodes.barcode_events_mixin']

    product_id = fields.Many2one('product.product')
    product_name = fields.Char()
    product_price = fields.Float()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_name = self.product_id.display_name
            pricelist_id = self.env['ir.config_parameter'].sudo().get_param("price_barcode.productpricelist", '1')
            pricelist = self.env['product.pricelist'].browse(int(pricelist_id))
            partner = self.env.context.get('partner')
            quantity = self.env.context.get('quantity', 1.0)
            prices = {}
            if pricelist:
                quantities = [quantity] * len(self)
                partners = [partner] * len(self)
                prices = pricelist.get_products_price(self.product_id, quantities, partners)
            self.product_price = prices.get(self.product_id.id , 0)
        else:
            self.product_name = "Escanee un producto"
            self.product_price = 0

    def on_barcode_scanned(self, barcode):
        product = self.env[
            'product.product'].search([('barcode', '=', barcode)], limit=1)
        if product:
            self.product_id = product.id
        else:
            return {'warning': {
                'title': _('Wrong barcode'),
                'message': _(
                    'The barcode "%(barcode)s" doesn\'t'
                    ' correspond to a proper product.') % {'barcode': barcode}
            }}

