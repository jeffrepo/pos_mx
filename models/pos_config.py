# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    envio_salida_vencimiento_id = fields.Many2one('stock.picking.type','Envio de salida por vencimiento')