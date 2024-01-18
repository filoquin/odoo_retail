from requests import request
from odoo import fields, models, api

class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    def add_to_request(self):
        request = self._context.get('request', False)
        factor = self._context.get('factor', 1.0)
        if request:
            request_id = self.env['stock.supply.request'].browse(request)
            line = request_id.line_ids.filtered(
                lambda r: r.product_id.id == self.product_id.id)
            if len(line):
                line.quantity += self.qty * factor
            else:
                vals = {
                    'quantity': self.qty * factor,
                    'request_id': request_id.id,
                    'product_id': self.product_id.id,
                }
                self.env['stock.supply.request.line'].create(vals)

    def drop_form_request(self, qty=1):
        request = self._context.get('request', False)
        if request:
            request_id = self.env['stock.supply.request'].browse(request)
            line = request_id.line_ids.filtered(
                lambda r: r.product_id.id == self.product_id.id)
            if len(line) and line.quantity > 0:
                line.quantity -= qty
            else:
                line.unlink()


class ProductProduct(models.Model):

    _inherit = "product.product"

    supply_qty = fields.Float(
        'qty',
        compute="_compute_supply_qty",
        digits='Product Unit of Measure',
    )
    my_virtual_available = fields.Float(
        compute="_compute_my_quantities",
        string="My Stock",
    )


    def _compute_my_quantities(self):
        request = self._context.get('request', False)
        products =  self.env['product.product']
        if request:
            request_id = self.env['stock.supply.request'].browse(request)
            products = self.with_context(warehouse=request_id.calendar_id.orig_warehouse_id.id).filtered(lambda p: p.type != 'service')
            res = products._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
            for product in products:
                product.my_virtual_available = res[product.id]['virtual_available']
        # Services need to be set with 0.0 for all quantities
        services = self - products
        services.my_virtual_available = 0.0




    def _compute_supply_qty(self):
        request = self._context.get('request', False)
        if request:
            request_id = self.env['stock.supply.request'].browse(request)
            lines = request_id.line_ids.filtered(
                lambda r: r.product_id.id in self.ids)
            qtys = {x.product_id.id: x.quantity for x in lines}
            for product in self:
                product.supply_qty = qtys.get(product.id, 0)
        else:
            self.supply_qty = 0

    def add_to_request(self, qty=1):
        request = self._context.get('request', False)
        qty = self._context.get('factor', qty)
        if request:
            request_id = self.env['stock.supply.request'].browse(request)
            line = request_id.line_ids.filtered(
                lambda r: r.product_id.id == self.id)
            if len(line):
                line.quantity += qty
            else:
                vals = {
                    'quantity': qty,
                    'request_id': request_id.id,
                    'product_id': self.id,
                }
                self.env['stock.supply.request.line'].create(vals)

    def drop_form_request(self, qty=1):
        request = self._context.get('request', False)
        qty = self._context.get('factor', qty)

        if request:
            request_id = self.env['stock.supply.request'].browse(request)
            line = request_id.line_ids.filtered(
                lambda r: r.product_id.id == self.id)
            if len(line) and line.quantity > 0:
                line.quantity -= qty
            else:
                line.unlink()

    def popup_request(self):
        self.ensure_one()
        view_id = self.env.ref('supply_order.product_packaging_pop_view_tree')
        domain = [('product_id', '=', self.id)] 

        view = {
            'name': self.display_name,
            'view_mode': 'tree',
            'view_id': view_id.id,
            'res_model': 'product.packaging',
            'type': 'ir.actions.act_window',
            'context':{'request':self._context.get('request')},
            'domain': domain,
            'target': 'new',
        }
        return view
