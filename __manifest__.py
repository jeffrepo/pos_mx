# -*- coding: utf-8 -*-
{
    'name': "Pos mx",

    'summary': """ Pos mx""",

    'description': """
        Funciones extras para el módulo de POS
    """,

    'author': "JS",
    'website': "",

    'category': 'Uncategorized',
    'version': '1.0',

    'depends': ['point_of_sale'],

    'data': [
        'data/paperformat_ticket_stock.xml',
        'report/reporte_existencias.xml',
        'report/reporte_entrega_valores.xml',
        'reporte_entrega_valores_wizard.xml',
        'views/report.xml',
        'wizard/reporte_existencias_wizard.xml',
    ],
    'license': 'LGPL-3',
}
