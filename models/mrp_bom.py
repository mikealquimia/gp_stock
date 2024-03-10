# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = "mrp.bom.line"

    area_id = fields.Many2one('production.area', string="Departamento/Area")
    warehouse_id = fields.Many2one('stock.warehouse', string="Bodega a Solicitar")