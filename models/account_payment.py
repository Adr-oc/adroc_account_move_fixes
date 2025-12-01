# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.l10n_gt_extra.a_letras as a_letras


class AccountPayment(models.Model):
    _inherit = "account.payment"

    no_negociable = fields.Boolean(string="No Negociable", default=False)
    descripcion = fields.Char(string="Descripcion")
    nombre_impreso = fields.Char(string="Nombre Impreso")
    fecha_aplicacion = fields.Date(string="Fecha de Aplicacion")
    partner_app = fields.Many2one('res.partner', string="Contacto de Pago")

    def num_a_letras(self, amount):
        return a_letras.num_a_letras(abs(amount), completo=True)

    def current_date_format(self, date):
        """Convierte fecha a nombre de mes en espanol"""
        months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
        month = months[date.month - 1]
        return month

    def cuentas_contables(self):
        """Retorna las cuentas contables del asiento relacionado al pago"""
        move_id = self.move_id.id
        cuentas = self.env['account.move.line'].search([('move_id', '=', move_id)], order='id desc')

        movimientos = {'cuentas': []}

        for rec in cuentas:
            movimientos['cuentas'].append([
                rec.account_id.code,
                rec.account_id.name,
                abs(rec.debit),
                abs(rec.credit)
            ])

        return movimientos

    def codigo(self):
        """Extrae codigo de cuenta del diario"""
        try:
            codigo = self.journal_id.default_account_id.name.split()[3]
        except (IndexError, AttributeError):
            codigo = self.journal_id.default_account_id.code if self.journal_id.default_account_id else ''
        return codigo

    def tipo_pago(self):
        """Retorna el tipo de pago legible"""
        if self.payment_type == 'outbound':
            return 'Pago'
        elif self.payment_type == 'inbound':
            return 'Cobro'
        return ''
