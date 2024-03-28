# -*- coding: utf-8 -*-
{
    'name': "gp_stock",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'stock', 'hr', 'purchase_requisition','mrp'],
    'data': [
        'security/gp_stock_security.xml',
        'security/ir.model.access.csv',
        'views/production_areas_views.xml',
        'views/production_day_views.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'views/purchase_requisition_views.xml',
        'views/stock_picking_type_views.xml',
        'views/mrp_bom_views.xml',
        'views/stock_warehouse_views.xml',
        'views/product_category.xml',
        'views/product_template.xml',
        'wizard/set_components_product_request.xml',
        'reports/report_production_day_views.xml',
        'reports/product_request_stock_picking.xml',
    ],
}