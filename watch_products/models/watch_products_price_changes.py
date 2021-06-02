# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, tools

import logging

_logger = logging.getLogger(__name__)


class watch_products_price_changes(models.Model):
    _name = "watch.products.price.changes"
    _description = 'watch products price changes'
    _auto = False
    _order = "last_change desc"
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Articulo',
    )
    last_change = fields.Datetime(
        string='Ultimo Cambio',
    )
    list_price = fields.Float(
        string='Precio',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='supplier',
    )
    categ_id = fields.Many2one(
        'product.category',
        string='categ',
    )

    def init(self):
        tools.drop_view_if_exists(self._cr, 'watch_products_price_changes')
        self._cr.execute("""create view watch_products_price_changes as (
                select l.product_tmpl_id as id ,
                CASE WHEN min(ph.create_date) is not null THEN min(ph.create_date) ELSE l.write_date END as last_change ,
                l.product_tmpl_id, l.list_price,l.categ_id,l.partner_id
                from  (
                    select pt.id as product_tmpl_id , pt.list_price,max(h.create_date) as datetime, pt.write_date,pt.categ_id,max(si.name) as partner_id
                    from product_template pt 
                    left join product_sale_price_history h on h.product_tmpl_id=pt.id and h.list_price <> pt.list_price
                    left join product_supplierinfo si on pt.id = si.product_tmpl_id
                    where pt.active=True
                    group by pt.id , pt.list_price,pt.write_date,pt.categ_id
                ) l 
                left join product_sale_price_history ph  on l.product_tmpl_id = ph.product_tmpl_id and l.datetime < ph.create_date
                group by l.product_tmpl_id, l.list_price, l.write_date,l.categ_id,l.partner_id
            )""");
