from odoo import models, fields, api


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    markup = fields.Float(
        string='markup',
    )
