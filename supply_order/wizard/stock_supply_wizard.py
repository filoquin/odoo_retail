from odoo import fields, models, api, _


class StockSupplyWizard(models.Model):
    _name = 'stock.supply.wizard'
    _description = 'warehouse supply wizard'

    @api.model
    def default_get(self, default_fields):
        rec = super(StockSupplyWizard, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model == 'stock.picking':
            pickings = self.env[active_model].browse(active_ids)
            rec['filter_qty_available'] = all([x == 'done' for x in pickings.mapped('state')])
            rec['product_ids'] = [(6, 0,  pickings.mapped('move_lines.product_id').ids)]
            rec['warehouse_id'] = pickings.mapped('warehouse_id')[0].id
            rec['direction'] = 'outgoing'
        elif active_model == 'purchase.order':
            purchases = self.env[active_model].browse(active_ids)
            rec['filter_qty_available'] = all([x == 'done' for x in purchases.mapped('state')])
            rec['product_ids'] =[(6, 0,  purchases.mapped('order_line.product_id').ids)]
            rec['warehouse_id'] = pickings.mapped('pickings_type_id.warehouse_id')[0].id
            rec['direction'] = 'outgoing'
        elif active_model == 'stock.picking.type':
            picking_type = self.env[active_model].browse(active_ids)[0]
            rec['filter_qty_available'] = True
            rec['direction'] = picking_type.code
            rec['warehouse_id'] = picking_type.warehouse_id.id

        return rec

    name = fields.Char()
    warehouse_id = fields.Many2one('stock.warehouse')
    direction = fields.Selection([('incoming', 'Receipt'),('outgoing','Delivery')])
    rule_id = fields.Many2one('stock.supply.rule')
    calendar_id = fields.Many2one('stock.supply.calendar')
    product_ids = fields.Many2many('product.product')
    filter_qty_available = fields.Boolean()
    filter_autocomplete = fields.Boolean()

    def action_create_request(self):
        domain = []
        if len(self.product_ids):
            domain += [('id', 'in', self.product_ids.ids)]
        request_id = self.env['stock.supply.request'].create({
            'calendar_id':self.calendar_id.id,
            'rule_id':self.rule_id.id,
            'filter_qty_available': self.filter_qty_available,
            'domain': str(domain),
        })
        view_id = self.env.ref('supply_order.stock_supply_request_form')
        view = {
            'name': "Abastecimiento",
            'view_mode': 'form',
            'view_id': view_id.id,
            'view_type': 'form',
            'res_id': request_id.id,
            'res_model': 'stock.supply.request',
            'type': 'ir.actions.act_window',
            'target': 'self',
        }
        return view


    def action_open_wizard(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('new supply request'),
            'res_model': 'stock.supply.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('supply_order.stock_supply_wizard_view_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }