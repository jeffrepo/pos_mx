# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import time
from datetime import date
import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime

class PosmxReporteExistenciasWizard(models.TransientModel):
    _name = 'pos_mx.reporte_existencias.wizard'

    def _tienda_actual(self):
        tienda = False
        almacen_id = self.env.user.property_warehouse_id.id
        tienda_id = self.env['pos.config'].search([('warehouse_id','=',almacen_id)])
        if len(tienda_id) > 0:
            tienda = tienda_id
        return tienda

    tienda_id = fields.Many2one('pos.config', 'Tienda/Sucursal', default=_tienda_actual, required=True)

    def print_report(self):
        data = {
             'ids': [],
             'model': 'pos_mx.reporte_existencias.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('pos_mx.action_reporte_existencias').report_action(self, data=data)
