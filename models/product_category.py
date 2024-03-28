# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = "product.category"

    quality_control_test = fields.Many2many('ach.quality.control', string="Preguntas de Puntos de Control de Calidad")