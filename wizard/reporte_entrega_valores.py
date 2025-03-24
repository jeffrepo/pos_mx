# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time
import base64
import xlsxwriter
import io
import logging
from datetime import date
import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime

class reporte_entrega_valores_wizard(models.TransientModel):
    _name = 'pos_mx.reporte_entrega_valores.wizard'

    fecha_inicio = fields.Datetime('Fecha inicio')
    fecha_fin = fields.Datetime('Fecha fin')
    tienda_id = fields.Many2one('pos.config','Tienda/Sucursal',default=lambda self: self.env.user.pos_id.id)
    fecha_generacion = fields.Datetime('Fecha/Hora',default=fields.Datetime.now)

    def print_report(self):
        data = {
             'ids': [],
             'model': 'pos_mx.reporte_entrega_valores.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('pos_mx.action_reporte_entrega_valores').report_action(self, data=data)