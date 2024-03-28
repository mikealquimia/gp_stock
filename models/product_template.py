# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    options_sales = fields.Many2many('product.product', string="Productos Complementos")
    quality_control_test = fields.Many2many('ach.quality.control', string="Preguntas de Puntos de Control de Calidad")