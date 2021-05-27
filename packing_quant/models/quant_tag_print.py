# -*- coding: utf-8 -*-
from openerp import api, fields, models


import logging
_logger = logging.getLogger(__name__)


class quantTagPrint(models.TransientModel):
    _name = 'quant.tag_print'
    _description = 'quant tag print'

    @api.model
    def default_get(self, fields):
        res = super(quantTagPrint, self).default_get(fields)
        if 'active_ids' in self._context:
            vals = [(0, 0, {'product_id': x.product_id.id, 'qty': x.quantity})
                    for x in self.env['stock.quant'].browse(self._context['active_ids'])]
        res.update({'line_ids': vals})
        return res

    report_id = fields.Many2one(
        'ir.actions.report',
        string='Report',
        required=True,
        domain=[('model', '=', 'product.product'), ]
    )

    line_ids = fields.One2many(
        'quant.tag_print.line',
        'print_id',
        string='Lines',
    )

    def action_print(self):
        product_ids = []
        for line in self.line_ids:
            product_ids += [line.product_id.id for x in range(0, line.qty)]
        return self.report_id.report_action(product_ids)


class ProductTagPrintLine(models.TransientModel):
    _name = 'quant.tag_print.line'
    _description = 'product tag print line'

    print_id = fields.Many2one(
        'quant.tag_print',
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
