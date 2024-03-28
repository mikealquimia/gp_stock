# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductionArea(models.Model):
    _name = "production.area"
    _description = "Area de Producción"
    
    name = fields.Char(string="Área")
    sub_area = fields.Boolean(string="¿Utiliza Subareas?")
    
class ProductionSubarea(models.Model):
    _name = "production.subarea"
    _description = "Sub-area de Producción"
    
    name = fields.Char(string="Sub Área")
