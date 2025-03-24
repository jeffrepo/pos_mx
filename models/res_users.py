# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _

class Users(models.Model):
    _inherit = 'res.users'

    pos_id = fields.Many2one("pos.config", string="Punto de Venta")