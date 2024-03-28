# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    purchase_requisition = fields.Boolean(string="Check Purchase")
    production_area_check = fields.Boolean(string="Áreas de Producción")
    stock_picking_type_product_request = fields.Boolean(string='Albaran para Solicitar Materiales')
    product_request_warehouse = fields.Boolean(string='Albaran de Solicitud de Materiales')
    quality_control_test = fields.Many2many('ach.quality.control', string="Preguntas de Puntos de Control de Calidad")
