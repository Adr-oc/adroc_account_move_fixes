# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Tarifa/Pricelist",
        check_company=True,
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Si cambias la tarifa, solo las líneas nuevas serán afectadas. "
             "Usa el botón 'Actualizar Precios' para actualizar líneas existentes."
    )

    pricelist_warning = fields.Text(
        string="Advertencia de Tarifa",
        compute='_compute_pricelist_warning',
        help="Mensaje de advertencia cuando la tarifa cambió"
    )

    @api.depends('pricelist_id', 'invoice_line_ids', 'state', 'partner_id')
    def _compute_pricelist_warning(self):
        """Calcula el mensaje de advertencia de tarifa"""
        for move in self:
            # Solo mostrar en facturas de cliente en borrador con líneas
            if (move.state == 'draft' and
                move.move_type in ('out_invoice', 'out_refund') and
                move.invoice_line_ids and
                move.pricelist_id and
                move.partner_id):

                # Verificar si la tarifa del partner es diferente a la tarifa actual
                tarifa_partner = move.partner_id.property_product_pricelist
                if tarifa_partner and tarifa_partner != move.pricelist_id:
                    move.pricelist_warning = (
                        f"La tarifa de la factura ({move.pricelist_id.name}) es diferente "
                        f"a la tarifa del cliente ({tarifa_partner.name}). "
                        f"Los precios de las líneas podrían no estar actualizados. "
                        f"Haz clic en 'Actualizar Precios' para aplicar la tarifa actual."
                    )
                else:
                    move.pricelist_warning = False
            else:
                move.pricelist_warning = False

    @api.model_create_multi
    def create(self, vals_list):
        """Establece la tarifa automáticamente al crear la factura"""
        for vals in vals_list:
            # Solo para facturas de cliente sin tarifa definida
            if (vals.get('move_type') in ('out_invoice', 'out_refund') and
                vals.get('partner_id') and
                not vals.get('pricelist_id')):

                partner = self.env['res.partner'].browse(vals['partner_id'])
                if partner.property_product_pricelist:
                    vals['pricelist_id'] = partner.property_product_pricelist.id

        return super(AccountMove, self).create(vals_list)

    @api.onchange('partner_id')
    def _onchange_partner_id_pricelist(self):
        """Establece la tarifa cuando cambia el partner en la interfaz web"""
        if self.partner_id and self.move_type in ('out_invoice', 'out_refund'):
            # Obtener la tarifa del partner/contacto
            partner = self.partner_id
            # property_product_pricelist es un campo computed que busca automáticamente:
            # 1. Tarifa del contacto específico (si tiene una asignada directamente)
            # 2. Tarifa del partner padre (si el contacto no tiene)
            # 3. Tarifa de la compañía (si ninguno tiene)
            # Usamos property_product_pricelist que maneja correctamente la jerarquía
            nueva_tarifa = partner.property_product_pricelist

            # Asignar la tarifa primero
            if nueva_tarifa:
                # Si ya había líneas y la tarifa va a cambiar, preparar advertencia
                if (self.invoice_line_ids and
                    self.pricelist_id and
                    self.pricelist_id != nueva_tarifa):

                    self.pricelist_id = nueva_tarifa

                    # Verificar si el partner tiene advertencia de venta (Odoo 19: solo sale_warn_msg)
                    warnings = []
                    if self.partner_id.sale_warn_msg:
                        warnings.append(self.partner_id.sale_warn_msg)

                    # Agregar advertencia de cambio de tarifa
                    warnings.append(
                        f'La tarifa ha cambiado de "{self._origin.pricelist_id.name}" '
                        f'a "{nueva_tarifa.name}".\n\n'
                        f'Las líneas de factura existentes mantienen sus precios actuales. '
                        f'Si deseas actualizar los precios basados en la nueva tarifa, '
                        f'haz clic en el botón "Actualizar Precios".'
                    )

                    return {
                        'warning': {
                            'title': '⚠ Advertencia: Tarifa Cambiada',
                            'message': '\n\n'.join(warnings)
                        }
                    }
                else:
                    # Asignar tarifa sin advertencia de cambio
                    self.pricelist_id = nueva_tarifa

                    # Verificar si el partner tiene advertencia de venta (Odoo 19: solo sale_warn_msg)
                    if self.partner_id.sale_warn_msg:
                        return {
                            'warning': {
                                'title': _('Advertencia para %s') % self.partner_id.name,
                                'message': self.partner_id.sale_warn_msg
                            }
                        }
            else:
                # No hay tarifa del partner, pero verificar advertencia de venta
                if self.partner_id.sale_warn_msg:
                    return {
                        'warning': {
                            'title': _('Advertencia para %s') % self.partner_id.name,
                            'message': self.partner_id.sale_warn_msg
                        }
                    }

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id_warning(self):
        """Muestra advertencia cuando se cambia manualmente la tarifa"""
        if (self.invoice_line_ids and
            self.pricelist_id and
            self._origin.pricelist_id and
            self._origin.pricelist_id != self.pricelist_id):

            return {
                'warning': {
                    'title': '⚠ Advertencia: Tarifa Cambiada',
                    'message': (
                        f'Has cambiado la tarifa de "{self._origin.pricelist_id.name}" '
                        f'a "{self.pricelist_id.name}".\n\n'
                        f'Las líneas de factura existentes mantienen sus precios actuales. '
                        f'Si deseas actualizar los precios basados en la nueva tarifa, '
                        f'haz clic en el botón "Actualizar Precios".'
                    )
                }
            }

    def action_update_prices(self):
        """Actualiza los precios de todas las líneas basándose en la tarifa actual"""
        self.ensure_one()

        if not self.pricelist_id:
            raise UserError(_("Por favor selecciona una tarifa antes de actualizar los precios."))

        if self.state != 'draft':
            raise UserError(_("Solo puedes actualizar precios en facturas en borrador."))

        # Filtrar solo líneas de productos (no secciones ni notas)
        lines_to_update = self.invoice_line_ids.filtered(
            lambda line: line.product_id and line.display_type not in ('line_section', 'line_note')
        )

        for line in lines_to_update:
            line._update_price_from_pricelist()

        return True


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id', 'quantity', 'product_uom_id')
    def _onchange_product_pricelist(self):
        """Aplica el precio de la tarifa cuando se selecciona un producto"""
        if not self.product_id:
            return

        # Solo aplicar en facturas de cliente con tarifa
        if (self.move_id.move_type not in ('out_invoice', 'out_refund') or
            not self.move_id.pricelist_id):
            return

        # No aplicar en secciones o notas
        if self.display_type in ('line_section', 'line_note'):
            return

        # Obtener el precio de la tarifa (Odoo 19 API)
        pricelist = self.move_id.pricelist_id
        price = pricelist._get_product_price(
            product=self.product_id,
            quantity=self.quantity or 1.0,
            currency=self.move_id.currency_id,
            date=self.move_id.invoice_date or fields.Date.today(),
            uom=self.product_uom_id or self.product_id.uom_id,
        )

        # Solo actualizar si el precio es diferente de 0
        if price:
            self.price_unit = price

    def _update_price_from_pricelist(self):
        """Actualiza el precio de la línea basándose en la tarifa del move"""
        self.ensure_one()

        if not self.move_id.pricelist_id or not self.product_id:
            return

        # Solo aplicar en facturas de cliente
        if self.move_id.move_type not in ('out_invoice', 'out_refund'):
            return

        # Obtener el precio de la tarifa (Odoo 19 API)
        pricelist = self.move_id.pricelist_id
        price = pricelist._get_product_price(
            product=self.product_id,
            quantity=self.quantity or 1.0,
            currency=self.move_id.currency_id,
            date=self.move_id.invoice_date or fields.Date.today(),
            uom=self.product_uom_id or self.product_id.uom_id,
        )

        # Actualizar el precio unitario
        self.price_unit = price
