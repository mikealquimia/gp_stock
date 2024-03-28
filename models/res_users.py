# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = "res.users"

    production_area_id = fields.Many2one('production.area', string="Area de trabajo en producción")
