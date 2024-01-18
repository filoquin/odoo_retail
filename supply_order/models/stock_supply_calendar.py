from odoo import fields, models, api

class StockSupplyCalendar(models.Model):
    _name = 'stock.supply.calendar'
    _description = 'supply calendar'

    rule_id = fields.Many2one(
        'stock.supply.rule',
    )
    name = fields.Char(
        'Name',
        compute='_compute_name',
        store=True
    )
    deadline = fields.Datetime(
        string='Date',
        required=True
    )
    request_deadline = fields.Datetime(
        string='Request deadline'
    )
    preparation_deadline = fields.Datetime(
        string='Preparation deadline'
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        required=True,
        related='rule_id.warehouse_id'
    )
    request_ids = fields.One2many(
        'stock.supply.request',
        'calendar_id',
        string='request',
    )
    orig_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='From Warehouse',
        required=True,
        related='rule_id.orig_warehouse_id'
    )
    route_ids = fields.Many2many(related='rule_id.route_ids')
    company_id = fields.Many2one(
        'res.company',
        default= lambda self: self.env.company
    )    
    @api.depends( 'warehouse_id', 'deadline')
    def _compute_name(self):
        for calendar in self:
            calendar.name = '%s %s' % (calendar.warehouse_id.name, fields.Datetime.to_string(calendar.deadline))

    def action_new_request(self):
        self.ensure_one()
        request_id = self.env['stock.supply.request'].create(
            {'calendar_id': self.id, 'rule_id': self.rule_id.id,'domain': self.rule_id.domain,})
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
