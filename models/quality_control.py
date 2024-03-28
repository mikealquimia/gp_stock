# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AchQualityControl(models.Model):
    _name = "ach.quality.control"
    _description = "Quality COntrol"

    name = fields.Char('Pregunta', required=True)
    production_area_id = fields.Many2one('production.area', string="Area", required=True)

class PointQualityControl(models.Model):
    _name = "point.quality.control"
    _description = "Point Quality Control"

    name = fields.Char(string="Correlativo")
    user_id = fields.Many2one('res.users', string="Usuario de Control")
    production_area_id = fields.Many2one('production.area', string="Area")
    employee_id = fields.Many2one('hr.employee', string="Empleado")
    date_start = fields.Datetime(string="Inicio")
    date_end = fields.Datetime(string="Final")
    stock_picking_id = fields.Many2one('stock.picking', string='Albarán')
    reason_lost_quality = fields.Text(string="Razón de Perdida de Control de Calidad")
    preventive_action = fields.Text(string="Accíon Preventiva")
    corrective_action = fields.Text(string="Acción Correctiva")
    create_wake_up_call = fields.Boolean(string="Crear llamada de atención")
    stock_picking_type_lost_quality = fields.Selection([('error','Vale de error'),('warranty','Garantia')], string="Tipo de documento")
    resume = fields.Text(string="Resumen")
    state = fields.Selection([('disapproved', 'Reprobado'),('approved', 'Aprobado')])
    count_stock_picking_error = fields.Integer(string='Vales de error', compute='_compute_stock_picking')
    count_stock_picking_warranty = fields.Integer(string='Garantrias', compute='_compute_stock_picking')

    @api.one
    def _compute_stock_picking(self):
        for rec in self:
            rec.count_stock_picking_error = len(self.env['stock.picking'].sudo().search([('point_quality_control','=',rec.id),('picking_type_id','=',rec.stock_picking_id.picking_type_id.warehouse_id.picking_type_error_id.id)]))
            rec.count_stock_picking_warranty = len(self.env['stock.picking'].sudo().search([('point_quality_control','=',rec.id),('picking_type_id','=',rec.stock_picking_id.picking_type_id.warehouse_id.picking_type_warranty_id.id)]))

    @api.multi
    def action_stock_picking_error(self):
        stock_picking_ids = self.env['stock.picking'].sudo().search([('point_quality_control','=',self.id),('picking_type_id','=',self.stock_picking_id.picking_type_id.warehouse_id.picking_type_error_id.id)])
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', stock_picking_ids.ids]],
            "name": "Vales de Error",
        }

    @api.multi
    def action_stock_picking_warranty(self):
        stock_picking_ids = self.env['stock.picking'].sudo().search([('point_quality_control','=',self.id),('picking_type_id','=',self.stock_picking_id.picking_type_id.warehouse_id.picking_type_warranty_id.id)])
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', stock_picking_ids.ids]],
            "name": "Garantias",
        }

    @api.model
    def create(self, vals):
        next_correlative = len(self.env['point.quality.control'].search([]))
        res = super(PointQualityControl, self).create(vals)
        res.write({'name':'QC'+str(next_correlative+1)})
        return res