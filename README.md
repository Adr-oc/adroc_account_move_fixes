# Adroc Account Move Fixes

Módulo para fixes y features generales de contabilidad.

## Características

### 1. Advertencias de Partner en Facturas

Este módulo muestra las advertencias configuradas en el partner cuando se crea o modifica una factura de cliente, similar a como funciona en las órdenes de venta.

Cuando asignas un partner que tiene `sale_warn = 'warning'` configurado, aparecerá un wizard/popup mostrando el mensaje de advertencia del partner (`sale_warn_msg`).

**Nota**: Esta advertencia solo aparece cuando se asigna el partner desde la interfaz web. Si la factura se crea programáticamente, el onchange no se ejecuta.

### 2. Soporte de Tarifas/Pricelist en Facturas

Este módulo agrega funcionalidad de tarifas (pricelist) a las facturas de cliente (`account.move`), similar a como funciona en las órdenes de venta.

#### Funcionalidades:

- **Campo de Tarifa**: Se agrega un campo "Tarifa/Pricelist" en las facturas de cliente que se calcula automáticamente basado en la tarifa del cliente.

- **Advertencia de Cambio**: Cuando cambias la tarifa en una factura existente, aparece un botón "Actualizar Precios" para aplicar los nuevos precios a las líneas existentes.

- **Actualización de Precios**: Al hacer clic en "Actualizar Precios", todas las líneas de la factura se actualizan con los precios de la tarifa seleccionada.

#### Cómo usar:

1. Abre una factura de cliente (Facturas de Cliente > Crear)
2. Selecciona un cliente (automáticamente cargará su tarifa)
3. Agrega productos a las líneas de factura
4. Si cambias la tarifa, aparecerá el botón "Actualizar Precios"
5. Haz clic en "Actualizar Precios" para aplicar la nueva tarifa a todas las líneas

#### Notas:

- Solo funciona en facturas de cliente (`out_invoice`, `out_refund`)
- Solo se puede actualizar precios en facturas en estado "Borrador"
- El campo de tarifa solo es visible si tienes activado el grupo "Tarifas" (product.group_product_pricelist)

## Instalación

1. Reinicia Odoo:
   ```bash
   docker-compose restart
   ```

2. Actualiza la lista de aplicaciones en Odoo (Modo Desarrollador):
   - Ve a Aplicaciones
   - Haz clic en "Actualizar lista de aplicaciones"
   - Busca "Adroc Account Move Fixes"
   - Instala el módulo

## Dependencias

- `account`: Módulo de contabilidad
- `product`: Módulo de productos (para tarifas)
- `sale`: Módulo de ventas

## Autor

Adroc

## Versión

1.0
