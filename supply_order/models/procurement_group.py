from odoo import fields, models, api

class ProcurementGroup(models.Model):

    _inherit = 'procurement.group'

    def _get_orderpoint_domain(self, company_id=False):
        domain = super()._get_orderpoint_domain(company_id)
        procurement_id = self.env.context.get('only_procurement', False)
        if procurement_id:
            domain += [('id', '=', procurement_id)]
        return domain

