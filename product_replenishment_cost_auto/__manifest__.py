# -*- coding: utf-8 -*-
{
    'name': "product replenishment cost auto",

    'summary': """Automatiza la implementacion de las reglas de costo""",

    'description': """
        Automatiza la implementacion de las reglas de costo
    """,

    'author': "filoquin",
    'website': "http://www.blancoamor.com",

    'category': 'product',
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['product_replenishment_cost'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/replenshiment_cost_rule.xml',
    ],

}
