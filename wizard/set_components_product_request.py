# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round

class StockMoveProductRequest(models.TransientModel):
    _name = 'stock.move.product.request'
    _description = 'Set Component for product request'

    name = fields.Char(string='name')
    product_id = fields.Many2one('product.product', string="Producto Vendido")
    line_ids = fields.Many2many('stock.move', string="Componentes")

    def set_component(self):
        return