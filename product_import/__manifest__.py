# -*- coding: utf-8 -*-
{
    "name": "Product import",
    "version": "13.0.1.0.0",
    "category": "sales",
    "description": """
Product import
======================
Add configurable templates for import products from  files    """,
    "author": "Filoquin",
    "website": "http://sipecu.com.ar",
    "depends": ["product", "web_widget_x2many_2d_matrix", "sale", "queue_job"],
    "installable": True,
    'external_dependencies':{
            'python': ['xlrd'],
        },    
    "data": [
        "security/ir.model.access.csv",
        "views/import_config.xml",
        "views/import.xml",
        "views/product.xml",
    ],
    "images": [],
    "auto_install": False,
}
