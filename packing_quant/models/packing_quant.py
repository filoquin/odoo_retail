# -*- coding: utf-8 -*-

from odoo import models, fields, api
from math import ceil
import logging

_logger = logging.getLogger(__name__)


class packing_quant(models.TransientModel):
    _name = 'stock.packing_quant'
    _description = 'packing quant'

    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True,
    )
    packaging_type_id = fields.Many2one(
        'product.packaging.type',
        string='packaging type',
        required=True,
    )
    product_ids = fields.Many2many(
        'product.product',
        string='Products',
    )
    report_id = fields.Many2one(
        'ir.actions.report',
        string='Report',
        required=True,
    )

    def action_print_labels(self):
        leaf = []
        leaf.append(('product_id.packaging_ids.packaging_type_id',
                     '=', self.packaging_type_id.id))
        leaf.append(('location_id', 'child_of', self.location_id.id))
        if len(self.product_ids):
            leaf.append(('product_id', 'in', self.product_ids.ids))

        quants = self.env['stock.quant'].search(leaf)
        packs_ids = []
        for quant in quants:
            packaging_id = quant.product_id.packaging_ids.filtered(
                lambda p: p.packaging_type_id.id == self.packaging_type_id.id)
            _logger.info(packaging_id)
            q = ceil(quant.quantity / packaging_id[0].qty)

            packs_ids += [packaging_id[0].id for x in range(
                0, q)]
        return self.report_id.report_action(packs_ids)
