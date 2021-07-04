# -*- coding: utf-8 -*-
import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class productTagPrint(models.TransientModel):
    _name = 'product.tag_print'
    _description = 'quant tag print'

    @api.model
    def default_get(self, fields):
        res = super(productTagPrint, self).default_get(fields)
        if 'active_ids' in self._context:
            vals = [(0, 0, {'product_id': x.id, 'qty': x.qty_available or 1})
                    for x in self.env['product.product'].browse(self._context['active_ids'])]
        res.update({'line_ids': vals})
        return res

    report_id = fields.Many2one(
        'ir.actions.report',
        string='Report',
        required=True,
        domain=[
            ('model', '=', 'product.product'),
            ('binding_model_id', '!=', False),
            ]
        )

    line_ids = fields.One2many(
        'product.tag_print.line',
        'print_id',
        string='Lines',
    )

    def action_print(self):
        product_ids = []
        for line in self.line_ids:
            product_ids += [line.product_id.id for x in range(0, line.qty)]
        return self.report_id.report_action(product_ids)


class ProductTagPrintLine(models.TransientModel):
    _name = 'product.tag_print.line'
    _description = 'product tag print line'

    print_id = fields.Many2one(
        'product.tag_print',
        string='print',
    )
    product_id = fields.Many2one(
        'product.product',
        string='product',
    )
    qty = fields.Integer(
        string='qty',
        default=1,
    )
