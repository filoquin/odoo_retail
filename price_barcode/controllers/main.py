# -*- coding: utf-8 -*-
import logging
import werkzeug
import werkzeug.utils


from odoo import http
from odoo.exceptions import AccessError
from odoo.http import  request

_logger = logging.getLogger(__name__)

class prices(http.Controller):


    # ideally, this route should be `auth="user"` but that don't work in non-monodb mode.
    @http.route('/prices', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        #ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        try:
            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('price_barcode.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
