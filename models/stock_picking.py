# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
import logging
import pytz
from datetime import datetime, timedelta
from lxml import etree
import re

class Picking(models.Model):
    _inherit = "stock.picking"

    def verificar_productos_vencidos_hoy(self):
        stock_quant = self.env['stock.quant'].sudo().search([('quantity','>',0),('removal_date','!=',False)])
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hoy = datetime.now().astimezone(timezone).strftime('%Y-%m-%d')
        # Sumarle un dia a la fecha de HOY

        dia_actual = datetime.now().astimezone(timezone).strftime('%d')
        mes_ao_actual = datetime.now().astimezone(timezone).strftime('%Y-%m')
        dia_mañana = int(dia_actual) + 0
        if dia_mañana<10:
            dia_mañana = '0'+str(dia_mañana)
        fecha_mañana = str(mes_ao_actual)+'-'+str(dia_mañana)
        inventario = {}
        ubicacion_actual = False
        if stock_quant:
            for linea in stock_quant:
                if linea.location_id.id not in inventario:
                    inventario[linea.location_id.id] = {'productos':[],'bodega':linea.location_id}
                if linea.lot_id and linea.lot_id.expiration_date and (linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') == fecha_mañana or linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') <= fecha_mañana or linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') == fecha_hoy):
                    inventario[linea.location_id.id]['productos'].append(linea)

            tiendas_ids = self.env['pos.config'].search([('envio_salida_vencimiento_id','!=', False)])
            # picking_ids = self.env['stock.picking.type'].search([('tipo_operacion_caducidad_id','!=', False)])
            if tiendas_ids:
                for tienda in tiendas_ids:
                    ubicacion_actual = tienda.envio_salida_vencimiento_id.default_location_src_id
                    if tienda.envio_salida_vencimiento_id.default_location_src_id.id in inventario:
                        destino_id = tienda.envio_salida_vencimiento_id.default_location_dest_id
                        tipo_envio_id = tienda.envio_salida_vencimiento_id
                        # logging.warn(inventario[tienda.picking_type_id.default_location_src_id.id]['productos'])
                        if len(inventario[tienda.envio_salida_vencimiento_id.default_location_src_id.id]['productos']) > 0:
                            stock_quant_lista = []
                            logging.warning('salida vencimiento')
                            logging.warning(tienda.envio_salida_vencimiento_id.id)
                            envio = {
                                'picking_type_id': tienda.envio_salida_vencimiento_id.id,
                                'location_id': ubicacion_actual.id,
                                'location_dest_id': destino_id.id,
                                'immediate_transfer': True,
                            }
                            envio_id = self.env['stock.picking'].create(envio)
                            for quant in inventario[tienda.envio_salida_vencimiento_id.default_location_src_id.id]['productos']:
                                # linea_envio = {
                                #     'product_id': quant.product_id.id,
                                #     'location_id': ubicacion_actual.id,
                                #     'product_uom_id': quant.product_id.uom_id.id,
                                #     'location_dest_id': salida.default_location_dest_id.id,
                                #     'lot_id': quant.lot_id.id,
                                #     'picking_id': envio_id.id
                                # }
                                move = {
                                    'product_id': quant.product_id.id,
                                    'name': quant.product_id.name,
                                    'product_uom': quant.product_id.uom_id.id,

                                    'location_id': ubicacion_actual.id,
                                    'product_uom_qty': quant.quantity,
                                    'location_dest_id': destino_id.id,
                                    # 'lot_id': quant.lot_id.id,
                                    'picking_id': envio_id.id
                                }
                                move_id = self.env['stock.move'].create(move)
                                move['move_id'] = move_id.id
                                move['lot_id'] = quant.lot_id.id
                                move['product_uom_qty'] = quant.quantity
                                stock_quant_lista.append(move)

                            # envio_id.action_confirm()
                            # envio_id.action_assign()
                            for quant in stock_quant_lista:
                                ml = {
                                    'product_id': quant['product_id'],
                                    'location_id': ubicacion_actual.id,
                                    'product_uom_id': quant['product_uom'],
                                    'location_dest_id': destino_id.id,
                                    'lot_id': quant['lot_id'],
                                    'move_id': quant['move_id'],
                                    'qty_done': quant['product_uom_qty'],
                                    'picking_id':envio_id.id,
                                }
                                move_line_id = self.env['stock.move.line'].create(ml)
                            envio_id.action_assign()
                            # envio_id.button_validate()
                            # envio_id.button_validate()

                            # envio_id.button_validate()

        return inventario

    def verificar_productos_vencidos(self):
        stock_quant = self.env['stock.quant'].sudo().search([('quantity','>',0),('removal_date','!=',False)])
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hoy = datetime.now().astimezone(timezone).strftime('%Y-%m-%d')
        # Sumarle un dia a la fecha de HOY

        dia_actual = datetime.now().astimezone(timezone).strftime('%d')
        mes_ao_actual = datetime.now().astimezone(timezone).strftime('%Y-%m')
        dia_mañana = int(dia_actual) + 1
        if dia_mañana<10:
            dia_mañana = '0'+str(dia_mañana)
        fecha_mañana = str(mes_ao_actual)+'-'+str(dia_mañana)
        inventario = {}
        ubicacion_actual = False
        if stock_quant:
            for linea in stock_quant:
                if linea.location_id.id not in inventario:
                    inventario[linea.location_id.id] = {'productos':[],'bodega':linea.location_id}
                if linea.lot_id and linea.lot_id.expiration_date and (linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') == fecha_mañana or linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') <= fecha_mañana or linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') == fecha_hoy):
                    inventario[linea.location_id.id]['productos'].append(linea)

            tiendas_ids = self.env['pos.config'].search([('envio_salida_vencimiento_id','!=', False)])
            # picking_ids = self.env['stock.picking.type'].search([('tipo_operacion_caducidad_id','!=', False)])
            if tiendas_ids:
                for tienda in tiendas_ids:
                    ubicacion_actual = tienda.envio_salida_vencimiento_id.default_location_src_id
                    if tienda.envio_salida_vencimiento_id.default_location_src_id.id in inventario:
                        destino_id = tienda.envio_salida_vencimiento_id.default_location_dest_id
                        tipo_envio_id = tienda.envio_salida_vencimiento_id
                        # logging.warn(inventario[tienda.picking_type_id.default_location_src_id.id]['productos'])
                        if len(inventario[tienda.envio_salida_vencimiento_id.default_location_src_id.id]['productos']) > 0:
                            stock_quant_lista = []
                            envio = {
                                'picking_type_id': tienda.envio_salida_vencimiento_id.id,
                                'location_id': ubicacion_actual.id,
                                'location_dest_id': destino_id.id,
                                'immediate_transfer': True,
                            }
                            envio_id = self.env['stock.picking'].create(envio)
                            for quant in inventario[tienda.envio_salida_vencimiento_id.default_location_src_id.id]['productos']:
                                # linea_envio = {
                                #     'product_id': quant.product_id.id,
                                #     'location_id': ubicacion_actual.id,
                                #     'product_uom_id': quant.product_id.uom_id.id,
                                #     'location_dest_id': salida.default_location_dest_id.id,
                                #     'lot_id': quant.lot_id.id,
                                #     'picking_id': envio_id.id
                                # }
                                move = {
                                    'product_id': quant.product_id.id,
                                    'name': quant.product_id.name,
                                    'product_uom': quant.product_id.uom_id.id,

                                    'location_id': ubicacion_actual.id,
                                    'product_uom_qty': quant.quantity,
                                    'location_dest_id': destino_id.id,
                                    # 'lot_id': quant.lot_id.id,
                                    'picking_id': envio_id.id
                                }
                                move_id = self.env['stock.move'].create(move)
                                move['move_id'] = move_id.id
                                move['lot_id'] = quant.lot_id.id
                                move['product_uom_qty'] = quant.quantity
                                stock_quant_lista.append(move)

                            # envio_id.action_confirm()
                            # envio_id.action_assign()
                            for quant in stock_quant_lista:
                                ml = {
                                    'product_id': quant['product_id'],
                                    'location_id': ubicacion_actual.id,
                                    'product_uom_id': quant['product_uom'],
                                    'location_dest_id': destino_id.id,
                                    'lot_id': quant['lot_id'],
                                    'move_id': quant['move_id'],
                                    'qty_done': quant['product_uom_qty'],
                                    'picking_id':envio_id.id,
                                }
                                move_line_id = self.env['stock.move.line'].create(ml)
                            envio_id.action_assign()
                            # envio_id.button_validate()
                            # envio_id.button_validate()

                            # envio_id.button_validate()

        return inventario
