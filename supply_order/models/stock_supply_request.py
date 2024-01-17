from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context
from odoo.tools import safe_eval


class StockSupplyRequest(models.Model):
    _name = 'stock.supply.request'
    _description = 'warehouse supply request'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Name',
        default="supply"
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('send', 'Send'), ('queued', 'Queued'),
         ('done', 'Done'), ('cancel', 'Cancel')],
        string='State',
        default='draft',
    )
    calendar_id = fields.Many2one(
        'stock.supply.calendar',
        string='Calendar',
    )
    rule_id = fields.Many2one(
        'stock.supply.rule',
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user.id,
    )
    send_date = fields.Datetime(
        string='Date',
    )
    line_ids = fields.One2many(
        'stock.supply.request.line',
        'request_id',
        string='lines',
    )
    notes = fields.Text(
        string='Notes',
    )
    last_recompute_available = fields.Datetime(
        string='last recompute available',
    )
    request_picking_ids = fields.Many2many(
        'stock.picking',
        compute="_compute_request_picking_ids"
    )
    domain = fields.Char()
    procurement_group_id = fields.Many2one('procurement.group')
    filter_qty_available = fields.Boolean(
        default=True
    )

    def _compute_request_picking_ids(self):
        with_procurement = self.filtered('procurement_group_id')
        for record in with_procurement:
            record.request_picking_ids = self.env['stock.picking'].search([('group_id', '=', record.procurement_group_id.id)])
        (self - with_procurement).request_picking_ids = False

    def action_send(self):
        now = datetime.now()
        request_limit = fields.Datetime.from_string(
            self.calendar_id.request_deadline)
        if now > request_limit: # and (not g1 or not g2):
            raise ValidationError('Se vencio el limite de pedido')

        self.write({'state': 'send', 'send_date': fields.Datetime.now(),
                    'user_id': self.env.user.id,
                    'name':  self.env['ir.sequence'].next_by_code('supply.req')})

    def action_start_request(self):
        self.ensure_one()
        self.recompute_available()
        view_id = self.env.ref('supply_order.product_supply_view_kanban')
        search_view_id = self.env.ref('supply_order.product_supply_view_search')
        domain = safe_eval(self.rule_id.domain or '[]')
        if self.filter_qty_available:
            domain += [('qty_available', '>', 0)]
        product_ids = self.env['product.product'].with_context({'warehouse': self.calendar_id.orig_warehouse_id.id}).search(domain)

        view = {
            'name': self.calendar_id.display_name,
            'view_mode': 'kanban',
            'view_id': view_id.id,
            'search_view_id':search_view_id.id,
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'context':{'warehouse': self.calendar_id.orig_warehouse_id, 'calendar_id': self.calendar_id.id, 'request':self.id},
            'domain': [('id', 'in', product_ids.ids)],
            'target': 'self',
        }
        return view


    def action_cancel(self):
        self.state = 'cancel'

    def recompute_available(self):
        self.line_ids._get_virtual_available()
        self.last_recompute_available = fields.Datetime.now()

    def action_done(self):
        for request_id in self:
            if all([x in ['done','cancel'] for x in  request_id.request_picking_ids.mapped('state')]):
                request_id.state = 'done'

    def action_queue(self):
        for request_id in self:
            if len(request_id.line_ids) < 1:
                request_id.state = 'cancel'
                return
            values = request_id._prepare_run_values()
            for request_line in request_id.line_ids:

                uom_reference = request_line.product_id.uom_id
                #self.quantity = self.product_uom_id._compute_quantity(self.quantity, uom_reference)
                try:
                    self.env['procurement.group'].with_context(clean_context(self.env.context)).run([
                        self.env['procurement.group'].Procurement(
                            request_line.product_id,
                            request_line.quantity,
                            uom_reference,
                            request_id.calendar_id.warehouse_id.lot_stock_id,  # Location
                            request_id.calendar_id.name,  # Name
                            request_id.name,  # Origin
                            request_id.calendar_id.warehouse_id.company_id,
                            values
                        )
                    ])
                    request_id.procurement_group_id = values['group_id'].id
                except UserError as error:
                    raise UserError(error)
            request_id.state = 'queued'

    def _prepare_run_values(self):
            replenishment = self.env['procurement.group'].with_context(force_company=self.calendar_id.company_id.id).create({
                'partner_id': self.user_id.partner_id.id,
            })

            values = {
                'warehouse_id': self.calendar_id.warehouse_id,
                'route_ids': self.calendar_id.route_ids if self.calendar_id.route_ids else self.env['stock.location.route'].search([]),
                'date_planned': self.calendar_id.preparation_deadline,
                'group_id': replenishment,
            }
            return values


class StockSupplyRequestLine(models.Model):
    _name = 'stock.supply.request.line'
    _description = 'warehouse supply request line'

    quantity = fields.Float(
        string='quantity',
        default=1,
    )
    request_id = fields.Many2one(
        'stock.supply.request',
        string='request',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    categ_id = fields.Many2one(
        'product.category',
        string='Category',
        related='product_id.categ_id',
    )

    list_price = fields.Float(
        string='list_price',
        related='product_id.list_price'
    )
    my_virtual_available = fields.Float(
        compute="_get_virtual_available",
        string="My Stock",
        store=True,
    )
    central_virtual_available = fields.Float(
        compute="_get_virtual_available",
        string="central Stock",
        store=True,
    )


    @api.onchange('product_id', 'request_id')
    @api.depends('product_id', 'request_id')
    def _get_virtual_available(self):

        for line in self:
            warehouse_id = line.request_id.calendar_id.warehouse_id.id
            orig_warehouse_id = line.request_id.calendar_id.orig_warehouse_id.id
            line.my_virtual_available = line.product_id.with_context(
                warehouse=warehouse_id).virtual_available
            line.central_virtual_available = line.product_id.with_context(
                warehouse=orig_warehouse_id).virtual_available


