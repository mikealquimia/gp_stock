# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    count_quality_control = fields.Integer(string="Llamadas de atención de Producción", compute='_compute_quality_control')

    @api.one
    def _compute_quality_control(self):
        for rec in self:
            rec.count_quality_control = len(self.env['point.quality.control'].sudo().search([('employee_id','=',rec.id),('create_wake_up_call','=',True)]))

    @api.multi
    def action_view_quality_control(self):
        point_quality_control = self.env['point.quality.control'].sudo().search([('employee_id','=',self.id),('create_wake_up_call','=',True)])
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "point.quality.control",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', point_quality_control.ids]],
            "name": "Puntos de Control de Calidad",
        }