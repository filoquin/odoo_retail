{
    'name': 'Watch products',
    'version': '13.0.0.1',
    'category': 'sale',
    'description': """
Productos seguidos
======================
Permite generar codigos de productos para estanterias por equipo de ventas.

    """,
    'author': 'Filoquin',
    'website': 'http://sipecu.com.ar',
    'depends': ['base', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/watch_products.xml',
        'views/watch_product_labels_report.xml',
        'views/watch_products_price_changes.xml',
        'report/labels.xml',
        # 'watching_products.xml',
        # 'views/watching_products_price_changes.xml',
        # 'report/label.xml',
        # 'report/etiqueta_producto.xml',
    ],
    "images": [],
    'post_init_hook': 'watch_post_init_hook',


    'auto_install': False,
}
