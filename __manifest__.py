# -*- coding: utf-8 -*-
{
    'name': 'Adroc Account Move Fixes',
    'version': '19.0.1.0.1',
    'category': 'Accounting',
    'summary': 'Fixes y features generales de contabilidad',
    'description': """
        Módulo para fixes y features generales de contabilidad:
        - Soporte de tarifas/pricelist en facturas (account.move)
        - Advertencia cuando cambia la tarifa
        - Botón para actualizar precios basados en la tarifa
        - Vouchers de pago (Voucher BI, Formato Assukargo)
        - Control de permisos para ver resumen de balance en conciliación bancaria
    """,
    'author': 'Adroc',
    'depends': [
        'account',
        'account_accountant',
        'product',
        'sale',
        'l10n_gt_extra',
        'invoice_gt',
    ],
    'data': [
        'security/groups.xml',
        'views/account_move_views.xml',
        'views/voucher_bi_payment.xml',
        'views/recibo_caja_statement.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adroc_account_move_fixes/static/src/js/bank_rec_kanban_renderer.js',
            'adroc_account_move_fixes/static/src/xml/bank_rec_kanban_renderer.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
