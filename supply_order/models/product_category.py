from odoo import fields, models, api


class ProductCategory(models.Model):


    _inherit = "product.category"

    supply_categ_id = fields.Many2one(
        'product.category',
        string='Third level',
        compute='_compute_supply_categ',
        inverse='_compute_supply_categ_inverse',
        store=True,
    )

    def _compute_supply_categ_inverse(self):
        pass

    @api.depends('parent_id')
    def _compute_supply_categ(self):
        for categ in self:
            parent = categ
            childs = []
            childs.append(parent.parent_id.id)
            while len(parent):
                parent = self.search(
                    [('id', '=', parent.parent_id.id)], limit=1)
                if len(parent) and parent.parent_id.id != False:
                    childs.append(parent.parent_id.id)

            if len(childs) > 3:
                categ.supply_categ_id = childs[-4]

            elif len(childs) > 2:
                categ.supply_categ_id = childs[-3]
            else:
                categ.supply_categ_id = categ.id
