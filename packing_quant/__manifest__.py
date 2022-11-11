# -*- coding: utf-8 -*-
{
    'name': "packing quant",

    'summary': """Imprimir etiquetas de paquete a demanda""",

    'description': """
        Imprimir etiquetas de paquete a demanda
    """,

    'author': "Filoquin",
    'website': "http://www.sipecu.com.ar",


    'category': 'Casa goro',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['product_packaging_type'],

    'data': [
        'views/packing_quant.xml',
        'views/quant_tag_print.xml',
        'views/product_tag_print.xml',
    ],
    'installable': False,
}
