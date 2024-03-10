# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    picking_type_product_request_id = fields.Many2one('stock.picking.type', string="Tipo de operación de Solicitudes de productos")