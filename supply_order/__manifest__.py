# -*- coding: utf-8 -*-
{
    'name': "supply orders",

    'summary': """
        Crea reglas especiales para abastecimiento""",

    'description': """
        Crea reglas especiales para abastecimiento
    """,

    'author': "filoquin",
    'website': "xx",

    'category': 'stock',
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/templates.xml',
        'views/stock_supply_calendar.xml',
        'views/stock_supply_request.xml',
        'views/stock_supply_rule.xml',
        'views/stock_picking_type.xml',
        'wizard/stock_supply_wizard.xml',
    ],
}
