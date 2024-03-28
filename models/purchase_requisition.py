# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"
    
    user_requisition = fields.Char(string="Solicitante(s)")
    
    