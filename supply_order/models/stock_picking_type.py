from odoo import fields, models, api


class StockPickingType(models.Model):


    _inherit = "stock.picking.type"
    
    def new_supply_request(self):
        self.ensure_one()
        active_ids = self.ids
        active_model = 'stock.picking.type'
        
        return self.env['stock.supply.wizard'].with_context(active_ids = active_ids, active_model=active_model).action_open_wizard()

