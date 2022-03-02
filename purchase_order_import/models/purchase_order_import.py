# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import xlrd
import base64

_logger = logging.getLogger(__name__)


class purchase_order_import(models.TransientModel):
    _name = 'purchase.order.import'
    _description = 'purchase order import'

    name = fields.Many2one(
        'purchase.order.import_config',
        string='Name',
    )
    start_line = fields.Integer(
        string='start line',
        related='name.start_line'
    )

    origin = fields.Char(
        string='Origin',
    )
    test = fields.Html(
        string='Test',
    )
    file_ids = fields.Many2many('ir.attachment', string="File")

    def process_xls(self):
        for file in self.file_ids:
            rows = []
            book = xlrd.open_workbook(
                file_contents=base64.decodestring(file.datas))
            sheet_names = book.sheet_names()
            sheet_names = [x.lower() for x in sheet_names]
            sheets = self.name.sheet.split(',')
            for sheet in sheets:
                if sheet.lower() in sheet_names or sheet.isnumeric():

                    index = int(
                        sheet) - 1 if sheet.isnumeric() else sheet_names.index(sheet.lower())
                    sheet = book.sheet_by_index(index)
                    for i in range(sheet.nrows):
                        r_temp = {}
                        if i < self.name.start_line:
                            continue

                        r = [cell.value for cell in sheet.row(i)]
                        rows.append(self.process_row(r))

                        # self.process_row(r)
            return rows

    def process_row(self, cells):
        res = {}
        if self.name.match_code in ['ean13']:
            code = str(int(cells[self.name.code_column - 1]))
            leaf = [('barcode', '=', code)]
        elif self.name.match_code in ['dun14']:
            code = str(cells[self.name.code_column - 1])
            leaf = [('packaging_ids.barcode', '=', code)]
        elif self.name.match_code in ['supplier']:
            code = str(cells[self.name.code_column - 1])
            leaf = [('seller_ids.product_code', '=', code)]

        elif self.name.match_code in ['default_code']:
            code = str(cells[self.name.code_column - 1])
            leaf = [('default_code', '=', code)]

        leaf += [('seller_ids.name', '=', self.name.partner_id.id)]
        product_id = self.env['product.product'].search(leaf)
        if len(product_id):
            res['state'] = 'match'
            res['product_id'] = product_id[0]
            res['product_name'] = product_id[0].with_context(partner_id=self.name.partner_id.id).display_name
            res['default_code'] = product_id[0].default_code
            if self.name.description_column:
                res['description'] = "%s %s" % (
                    cells[self.name.code_column - 1], cells[self.name.description_column - 1])
            else:
                res['description'] = res['product_name']

            res['qty'] = cells[self.name.qty_column - 1]
            if self.name.discount_column:
                res['discount'] = float(cells[self.name.discount_column - 1])

            if self.name.replace_comma:
                price = float(
                    cells[self.name.price_column - 1].replace(',', ''))
            else:
                price = float(cells[self.name.price_column - 1])
            if self.name.tax:
                res['unit_price'] = price / self.name.tax_coefficient
            else:
                res['unit_price'] = price
        if len(product_id) == 0:
            res['state'] = 'No'
            res['description'] = "%s %s" % (
                cells[self.name.code_column - 1], cells[self.name.description_column - 1])
        return res

    def tests(self):
        table = "<table class='table table-striped table-bordered'>"
        table += "<tr><th>S</th><th>Q</th><th>producto</th><th>Descripcion</th><th>Precio</th><th>Descuento</th></tr>"
        if self.name.file_format == 'xls':
            rows = self.process_xls()
            for row in rows:
                if row['state'] == 'match':
                    discount_column = row['discount'] if 'discount' in row else '--'
                    table += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                        row['state'], row['qty'], row['product_name'],
                        row['description'], row['unit_price'], discount_column)
                else:
                    table += '<tr><td>%s</td><td style="color:red;"  colspan="4">%s</td></tr>' % (
                        row['state'], row['description'])
        table += "</table>"
        self.test = table

    def create_purchase(self):
        purchase_order = self.env['purchase.order'].default_get([])
        purchase_order.update({'partner_id': self.name.partner_id.id,
                               'partner_ref': self.origin,
                               'order_line': []
                               })
        if self.name.file_format == 'xls':
            rows = self.process_xls()
            for row in rows:
                if row['state'] == 'match':
                    product_uom = row['product_id'].uom_po_id or row['product_id'].uom_id

                    vals = {
                        'date_planned': fields.Datetime.now(),
                        'product_id': row['product_id'].id,
                        'name': row['description'],
                        'product_uom': product_uom.id,
                        'price_unit': row['unit_price'],
                        'product_qty': row['qty']
                    }
                    if 'discount' in row:
                        vals['discount'] = row['discount']

                    purchase_order['order_line'].append((0, 0, vals))
        order = self.env['purchase.order'].create(purchase_order)

        view = {
            'name': "Orden de compra",
            'view_mode': 'form',
            'view_id': self.env.ref('purchase.purchase_order_form').id,
            'view_type': 'form',
            'res_model': 'purchase.order',
            'res_id': order.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'self',
            'domain': '[]',
        }
        return view


class purchase_order_import_config(models.Model):
    _name = 'purchase.order.import_config'
    _description = 'purchase order import config'

    name = fields.Char(
        string='Name',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    file_format = fields.Selection(
        [('xls', 'xls')],
        string='file format',
        required=True,
        default='xls'
    )
    csv_delimiter = fields.Char(
        string='csv delimiter',
        default=','
    )
    csv_quotechar = fields.Char(
        string='csv quotechar',
        default='"'
    )
    start_line = fields.Integer(
        string='start line',
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )
    match_code = fields.Selection(
        [('dun14', 'dun14'), ('ean13', 'ean13'),
         ('supplier', 'Supplier code'), ('default_code', 'internal code')],
        string='Match code',
        default='default_code'
    )
    code_column = fields.Integer(
        string='Code Column',
    )
    description_column = fields.Integer(
        string='Description Column',
    )
    qty_column = fields.Integer(
        string='Qty Column',
    )

    price_column = fields.Integer(
        string='Price Column',
    )
    discount_column = fields.Integer(
        string='discount Column',
    )
    tax = fields.Boolean(
        string='Con IVA',
    )
    tax_coefficient = fields.Float(
        string='valor Iva',
        default=1.21
    )

    sheet = fields.Char(
        string='Sheet',
    )
    replace_comma = fields.Boolean(
        string='Remplazar comas',
    )
