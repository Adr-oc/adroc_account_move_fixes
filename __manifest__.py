# -*- coding: utf-8 -*-
{
    'name': 'Adroc Account Move Fixes',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Fixes y features generales de contabilidad',
    'description': """
        Módulo para fixes y features generales de contabilidad:
        - Soporte de tarifas/pricelist en facturas (account.move)
        - Advertencia cuando cambia la tarifa
        - Botón para actualizar precios basados en la tarifa
        - Vouchers de pago (Voucher BI, Formato Assukargo)
    """,
    'author': 'Adroc',
    'depends': [
        'account',
        'product',
        'sale',
        'l10n_gt_extra',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/voucher_bi_payment.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
