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

from openerp import models, fields, api
from datetime import datetime, timedelta
import base64
import logging
import os 
import zipfile
import StringIO
from openerp.http import request

_logger = logging.getLogger(__name__)


class watching_products_changes(models.Model):
    _name = "watching.products.changes"
    _description = 'watching products changes'
    _inherit = "mail.thread"
    _order = 'date_from desc'

    state = fields.Selection(
        [('draft', 'draft'), ('prepared', 'prepared'),
         ('printed', 'printed'), ('unchanged', 'unchanged'),
         ('notprinted','not printed')],
        string='state',
        default='draft',
        track_visibility='onchange',

    )
    section_id = fields.Many2one(
        'crm.case.section',
        string='Equipo',
        required=True,
    )

    date_from = fields.Datetime(
        string='Desde la fecha',
        required=True,
    )
    date_to = fields.Datetime(
        string='Hasta la fecha',
        copy=False,
    )
    items_ids = fields.One2many(
        'watching.products.changes.item',
        'change_id',
        string='Items',
    )

    changes = fields.Boolean(
        string='Changes',
    )

    @api.model
    def cron_create_changes(self,default_date_from=False):
        self.search([('state','=','prepared')]).write({'state':'notprinted'})

        self._cr.execute("""select wp.section_id as id, max(date_to) - interval '3 hour' as last_print
                from product_watching_products  wp
                left join watching_products_changes wpc on wp.section_id = wpc.section_id  and  wpc.state in ('printed')
                where wp.active=True and wp.section_id is not Null 
                group by wp.section_id""")
        
        if not default_date_from : 
            default_date_from = fields.Datetime.to_string(
                datetime.now()- timedelta(days=1))
        
        
        for section in self._cr.dictfetchall():
            if section['last_print'] != None:
                date_from = section['last_print']
            else :
                date_from = default_date_from
           
            chang = self.create(
                {'section_id': section['id'], 'date_from': date_from})
            chang.action_get_items()

    @api.one
    def action_printed(self):
        self.state = 'printed'

    @api.one
    def download_all(self):
        filenames = []
        for attachment_id in self.items_ids:
            filecontent = base64.b64decode(attachment_id['datas'])
            filename = 'x_%s.pdf' %attachment_id.list_id['name']
            #content_type = 'application/x-pdf'
            attachment_file = open(str("/tmp/%s" % filename), "wb")
            attachment_file.write(filecontent)
            filenames.append('/tmp/%s'%filename)
        
        zip_filename = "%s.zip" % self.section_id['name'].replace(" ", "").lower()

        strIO = StringIO.StringIO()

        zip_file = zipfile.ZipFile(strIO, "w", zipfile.ZIP_DEFLATED)

        for file_path in filenames:
            file_dir, file_name = os.path.split(str(file_path))
            zip_path = os.path.join(self.section_id['name'].replace(" ", "").lower(), file_name)

            zip_file.write(file_path, zip_path)
        zip_file.close()
        return request.make_response(
                strIO.getvalue(),
                headers=[('Content-Type', 'application/x-zip-compressed'),
                         ('Content-Disposition', content_disposition(zip_filename))])
    @api.one
    def action_get_items(self):

        lists = self.env['product.watching.products'].search(
            [('section_id', '=', self.section_id.id), ('report', '!=', False)])

        changes = []
        items = []
        filenames = []
        for cur_obj in lists:
            product_ids = []
            date_to = fields.Datetime.now()
            for item in cur_obj.product_id:

                price_history_ids = self.env['product.sale.price.history'].search([
                    ('datetime', '<=', self.date_from),
                    ('product_template_id', '=', item.product_tmpl_id.id)],
                        order='datetime desc , id  desc', limit=1
                    )
                for history in price_history_ids:
                    if int(history.list_price) != int(item.list_price):
                        changes.append(u'%s anterior %s actualizado a %s' % (
                            item.default_code, history.list_price, item.list_price))
                        product_ids.append(item.id)
                        break

            if len(product_ids):

                report_obj = self.env['report']
                pr = self.env['product.product'].search(
                    [('id', 'in', product_ids)])

                pdf = report_obj.get_pdf(
                    pr, 'ba_watching_products.' + cur_obj.report)

                filename = '%s.pdf' %cur_obj.name.encode('ascii',errors='ignore').replace('/','').replace(' ', '_')

                attachment_file = open(str("/tmp/%s" % filename), "wb")
                attachment_file.write(pdf)
                filenames.append('/tmp/%s'%filename)


                ''''
                data, data_format = self.env.ref(
                    'ba_watching_products.' + cur_obj.report).render(product_ids)

                '''
                att_id = self.env['ir.attachment'].create({
                            'name': '%s.pdf' % cur_obj.name.replace(' ', '_'),
                            'type': 'binary',
                            'datas': base64.encodestring(pdf),
                            'datas_fname': '%s.pdf' % cur_obj.name.replace(' ', '_'),
                            'mimetype': 'application/x-pdf'
                })
                items.append((0, 0, {'list_id': cur_obj.id,
                                     'count': len(product_ids),
                                     'attachment_id': att_id.id

                                     }))

        self.items_ids = items
        if len(changes):

            strIO = StringIO.StringIO()

            zip_file = zipfile.ZipFile(strIO, "w", zipfile.ZIP_DEFLATED)

            for file_path in filenames:
                _logger.info(file_path )
                file_dir, file_name = os.path.split(str(file_path))
                zip_path = os.path.join(self.section_id['name'].replace(" ", "").lower(), file_name)
                zip_file.write(file_path, zip_path)
            zip_file.close()
            att_id = self.env['ir.attachment'].create({
                        'name': 'all_Files.zip',
                        'type': 'binary',
                        'datas': base64.encodestring(strIO.getvalue()),
                        'datas_fname': '%s.zip' % self.section_id.name.replace(' ', '_'),
                        'mimetype': 'application/x-zip-compressed',
                        'res_model': 'watching.products.changes',
                        'res_id': self.id,

            })



            self.write({'date_to': date_to,
                        'changes': True, 'state': 'prepared'})
            self.message_post(
                u'Cambios ' + " | ".join(changes), 'cambios')
        else:
            self.state = 'unchanged'


class watching_products_changes_item(models.Model):
    _name = "watching.products.changes.item"
    _description = 'watching products changes'

    change_id = fields.Many2one(
        'watching.products.changes',
        string='grupo',
    )

    list_id = fields.Many2one(
        'product.watching.products',
        string='Lista',
    )
    count = fields.Integer(
        string='Counts',
    )
    attachment_id = fields.Many2one('ir.attachment', 'tipo')
    datas = fields.Binary('pdf', related='attachment_id.datas')
'''
select  wp.id , wp.name, p.product_tmpl_id ,pt.name , section_id, h.list_price , pt.list_price
from product_watching_products wp
join watching_products_rel wpr on wp.id=wpr.list_id 
join product_product p on wpr.product_id = p.id
join product_template pt on p.product_tmpl_id = pt.id
join  product_sale_price_history h 
        on h.product_template_id= pt.id 
        and h.datetime > now() - interval '30 days' 
where  wp.active =True and h.list_price <> pt.list_price
'''