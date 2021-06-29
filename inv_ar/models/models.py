# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from dateutil.relativedelta import relativedelta
from lxml import etree
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):

    _inherit = 'account.move'


    def _get_name_invoice_report(self, report_xml_id):
        self.ensure_one()
        if self.l10n_latam_use_documents and self.company_id.country_id.code == 'AR':
            custom_report = {
                'account.report_invoice_document_with_payments': 'inv_ar.report_invoice_document_with_payments',
                'account.report_invoice_document': 'inv_ar.report_invoice_document',
            }
            return custom_report.get(report_xml_id) or report_xml_id
        return super()._get_name_invoice_report(report_xml_id)
