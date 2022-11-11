# -*- coding: utf-8 -*-
{
    'name': "product replenishment cost markup",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "filoquin",
    'website': "http://www.blancoamor.com",

    'category': 'product',
    'version': '13.0.0.0.1',

    'depends': ['product', 'product_replenishment_cost'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': False,
}
