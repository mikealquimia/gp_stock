# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    picking_type_product_request_id = fields.Many2one('stock.picking.type', string="Tipo de operación de Solicitudes de productos")
    quality_control_test = fields.Many2many('ach.quality.control', string="Preguntas de Puntos de Control de Calidad")
    picking_type_warranty_id = fields.Many2one('stock.picking.type', string="Tipo de operación Garantias")
    picking_type_error_id = fields.Many2one('stock.picking.type', string="Tipo de operación Vales de Error")
