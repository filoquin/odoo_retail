from odoo import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


def watch_post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info('start watch_post_init_hook')
    products = env['product.template'].search([])
    products._add_price_history()
    _logger.info('end watch_post_init_hook')
