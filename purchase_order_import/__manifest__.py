# -*- coding: utf-8 -*-
{
    'name': "purchase order import",

    'summary': """
        Importar ordenes de compra""",

    'description': """
        Importar ordenes de compra
    """,

    'author': "Filoquin",
    'website': "http://www.hormigag.ar",

    'category': 'puchase',
    'version': '13.0.0.1',

    'depends': ['purchase'],

    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_import.xml',
    ],
}
