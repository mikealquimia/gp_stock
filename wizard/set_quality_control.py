# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
import datetime
from datetime import date, datetime

class QualityControlRequest(models.TransientModel):
    _name = 'quality.control.request'
    _description = 'Set Quality Control'

    name = fields.Char(string='name')
    user_id = fields.Many2one('res.users', string="Usuario de Control")
    production_area_id = fields.Many2one('production.area', string="Area")
    employee_id = fields.Many2one('hr.employee', string="Empleado")
    date_start = fields.Datetime(string="Inicio")
    stock_picking_id = fields.Many2one('stock.picking', string='Albarán')
    question_line_ids = fields.One2many('test.quality.control', 'quality_id')
    validate_check = fields.Boolean(string="Valido para aprobar", compute='_compute_validate_check')
    view_check = fields.Boolean(string="Verificados todos los puntos", compute="_compute_validate_check")
    reason_lost_quality = fields.Text(string="Razón de Perdida de Control de Calidad")
    preventive_action = fields.Text(string="Accíon Preventiva")
    corrective_action = fields.Text(string="Acción Correctiva")
    create_wake_up_call = fields.Boolean(string="Crear llamada de atención")
    stock_picking_type_lost_quality = fields.Selection([('error','Vale de error'),('warranty','Garantia')], string="Tipo de documento")
    product_line_ids = fields.One2many('quality.control.request.product', 'quality_control_id', string="Productos")

    @api.onchange('question_line_ids')
    def _compute_validate_check(self):
        for rec in self:
            rec.validate_check = False if len(rec.question_line_ids.filtered(lambda l: l.control_quality == False)) > 0 else True
            rec.view_check = False if len(rec.question_line_ids.filtered(lambda l: l.view == False)) > 0 else True

    def validate(self):
        self.create_quanlity_control('approved')
        return

    def lost_quality(self):
        self.create_quanlity_control('disapproved')
        return

    def create_quanlity_control(self, state):
        if not self.employee_id:
            raise UserError("Debe establecer al empleado a calificar")
        resume = "Puntos Aprobados\n"
        for line in self.question_line_ids.filtered(lambda l: l.control_quality != False):
            resume += " - " + str(line.name) + "\n"
        resume += "Puntos Reprobados\n"
        for line_reprobed in self.question_line_ids.filtered(lambda l: l.control_quality == False):
            resume += " - " + str(line_reprobed.name) + "\n"
        vals = {'user_id':self.user_id.id,
                'production_area_id':self.production_area_id.id,
                'employee_id':self.employee_id.id,
                'date_start':self.date_start,
                'date_end':datetime.now(),
                'stock_picking_id':self.stock_picking_id.id,
                'resume':resume,
                'reason_lost_quality':self.reason_lost_quality,
                'preventive_action': self.preventive_action,
                'corrective_action': self.corrective_action,
                'create_wake_up_call': self.create_wake_up_call,
                'stock_picking_type_lost_quality': self.stock_picking_type_lost_quality,
                'state':state,
                }
        point_quality_control_id = self.env['point.quality.control'].create(vals)
        if self.stock_picking_type_lost_quality:
            qty_general = 0
            for line_preview in self.product_line_ids:
                qty_general += line_preview.qty
            if qty_general == 0:
                raise UserError('Debe de existir por lo menos una unidad para generar Garantia o Vale de Error')
            picking_type_id = False
            if self.stock_picking_type_lost_quality == 'warranty':
                picking_type_id = self.stock_picking_id.picking_type_id.warehouse_id.picking_type_warranty_id
            if self.stock_picking_type_lost_quality == 'error':
                picking_type_id = self.stock_picking_id.picking_type_id.warehouse_id.picking_type_error_id
            vals_stock_picking = {'picking_type_id': picking_type_id.id ,
                'scheduled_date': datetime.now(),
                'origin':point_quality_control_id.name + ' - ' + self.stock_picking_id.name,
                'product_request_state':'draft',
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': picking_type_id.default_location_dest_id.id,
                'point_quality_control':point_quality_control_id.id}
            picking_product_request_id = self.env['stock.picking'].create(vals_stock_picking)
            for line in self.product_line_ids:
                if line.qty > 0:
                    vals_line = {'name':'OT Generada por Control de Calidad',
                        'picking_id': picking_product_request_id.id,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.qty,
                        'product_uom': line.product_id.uom_id.id,
                        'location_id': picking_product_request_id.location_id.id,
                        'location_dest_id': picking_product_request_id.location_dest_id.id,
                        'state':'draft',
                        'is_locked':False,
                        'scrapped':False,
                        'reference':picking_product_request_id.name,}
                    self.env['stock.move'].create(vals_line)
            picking_product_request_id.action_confirm()

class TestQualityControl(models.TransientModel):
    _name = "test.quality.control"
    _description = "Quality COntrol Questions Temporal"

    name = fields.Char('Pregunta', required=True)
    production_area_id = fields.Many2one('production.area', string="Area", required=True)
    control_quality = fields.Boolean(string="Resultado")
    quality_id = fields.Many2one('quality.control.request', string='Punto de control')
    view = fields.Boolean(string="Verificado")

class QualityControlRequestProduct(models.TransientModel):
    _name = "quality.control.request.product"
    _description = "Quality COntrol Product"

    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', string="Producto")
    qty = fields.Integer(string="Resultado")
    uom_id = fields.Many2one('uom.uom', string='Unidad de Medida', related='product_id.uom_id')
    quality_control_id = fields.Many2one('quality.control.request', string="Verificado")