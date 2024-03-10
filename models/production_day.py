# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime

class ProductionDay(models.Model):
    _name = "production.day"
    _description = "Program Production"
        
    name = fields.Char(string="Programa de Producción")
    sequence = fields.Integer(string="Secuencia")
    production_area_id = fields.Many2one('production.area', string="Área de Producción")
    line_ids = fields.One2many('production.day.line', 'production_day', string="Líneas de producción")
    date_start = fields.Datetime(string="Fecha de Inicio")
    date_end = fields.Datetime(string="Fecha de Cierre")
    user_id = fields.Many2one('res.users', string="Encargado")
    previus_production_id = fields.Many2one('production.day', string="Anterior Programa")
    next_production_id = fields.Many2one('production.day', string="Siguiente Programa")
    state = fields.Selection([('draft','Borrador'),('progress', 'En Progreso'),('close', 'Cerrado')], default='draft')
    create_next_boolean = fields.Boolean(string="Creado siguiente")
    
    def action_close(self):
        self.write({'date_end': datetime.datetime.today(), 'state': 'close', 'create_next_boolean': True})
        return
    
    def action_progress(self):
        self.write({'state': 'progress', 'date_start': datetime.datetime.today()})
        return
    
    def action_open(self):
        self.write({'date_end': False, 'state': 'draft', 'date_start': False})
        return
    
    def create_next(self):
        sequence = 2
        production_area_id = self.production_area_id.id
        if self.previus_production_id:
            sequence = self.sequence +1
            production_area_id = self.production_area_id.id
        vals= {
            'name': str(self.production_area_id.name)+" #"+str(sequence),
            'sequence': sequence,
            'production_area_id': production_area_id,
            'previus_production_id': self.id,
        }
        next_production_day = self.env['production.day'].create(vals)
        for line in self.line_ids:
            if line.done_line == False:
                if line.cancel_line == False:
                    line.write({'production_day': next_production_day.id})
        self.write({'next_production_id': next_production_day.id, 'create_next_boolean': False})
        return
    
class ProductionDay(models.Model):
    _name = "production.day.line"
    _description = "Line Program Production"
    
    name = fields.Char(string="Nombre")
    production_day = fields.Many2one('production.day', string="Programa")
    stock_picking_id = fields.Many2one('stock.picking', string="Álbaran")
    origin_id = fields.Char(string="Origen")
    product_id = fields.Many2one('product.product', string="Producto")
    sub_area_ids = fields.Many2many('production.subarea', string="Subareas")
    product_qty = fields.Float(string="Cantidad")
    production_area_id = fields.Many2one('production.area', string="Área de Producción")
    date_in = fields.Datetime(string="Fecha de Ingreso")
    date_out = fields.Datetime(string="Fecha Terminado")
    employee_id = fields.Many2one('hr.employee', string="Encargado")
    done_line = fields.Boolean(string="Terminado")
    cancel_line = fields.Boolean(string="Cancelado")
    
    def action_done(self):
        self.write({'done_line': True, 'date_out': datetime.datetime.today()})
        
    def action_cancel(self):
        self.write({'cancel_line': True})
    
