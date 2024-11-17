# -*- encoding: utf-8 -*-

from odoo import api, models, fields
from datetime import date
import datetime
import time
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime
from operator import itemgetter
import pytz

class ReportExistencias(models.AbstractModel):
    _name = 'report.pos_mx.reporte_existencias'

    def productos_existencia(self, tienda_id):
        tiendas_id = self.env['pos.config'].search([('id','=',tienda_id[0])])

        ubicacion_id = tiendas_id.picking_type_id.default_location_src_id

        stock_id = self.env['stock.quant'].search([('location_id','=',ubicacion_id.id)], order='product_id asc')
        inventario = {}
        if stock_id:
            for linea in stock_id:
                if linea.lot_id and linea.lot_id.expiration_date:
                    if str(linea.product_id.categ_id.parent_id.id)+'/'+str(linea.product_id.categ_id.id) not in inventario:
                        inventario[str(linea.product_id.categ_id.parent_id.id)+'/'+str(linea.product_id.categ_id.id)] = {'productos': [],'categoria_padre': linea.product_id.categ_id.parent_id.name, 'categoria_hija': linea.product_id.categ_id.name }

                    inventario[str(linea.product_id.categ_id.parent_id.id)+'/'+str(linea.product_id.categ_id.id)]['productos'].append(linea)
                else:
                    if str(linea.product_id.categ_id.parent_id.id)+'/'+str(linea.product_id.categ_id.id) not in inventario:
                        inventario[str(linea.product_id.categ_id.parent_id.id)+'/'+str(linea.product_id.categ_id.id)] = {'productos': [],'categoria_padre': linea.product_id.categ_id.parent_id.name, 'categoria_hija': linea.product_id.categ_id.name }
                    inventario[str(linea.product_id.categ_id.parent_id.id)+'/'+str(linea.product_id.categ_id.id)]['productos'].append(linea)
        return inventario

    def obtener_tienda(self, tienda_id):
        tienda = self.env['pos.config'].search([('id','=',tienda_id[0])])
        return tienda;

    def fecha_hora_actual(self):
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hora = datetime.datetime.now().astimezone(timezone).strftime('%d/%m/%Y %H:%M:%S')
        return fecha_hora

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        tienda_id = data['form']['tienda_id']
        docs = self.env['pos.session'].browse(docids)
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'tienda_id': tienda_id,
            'productos_existencia': self.productos_existencia,
            'fecha_hora_actual': self.fecha_hora_actual,
            'obtener_tienda': self.obtener_tienda
        }
