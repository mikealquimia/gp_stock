# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    options_sales = fields.Many2many('product.product', string="Productos Complementos")