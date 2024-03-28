# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AchQualityControl(models.Model):
    _name = "ach.quality.control"
    _description = "Quality COntrol"

    name = fields.Char('Pregunta', required=True)
    production_are_id = fields.Many2one('production.area', string="Area", required=True)