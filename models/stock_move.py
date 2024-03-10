# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = "stock.move"
    
    production_area_ids = fields.Many2many('production.area', string="Areas de Producción")
    production_day_ids = fields.Many2many('production.day', string="Programas de Producción")
    production_create = fields.Boolean(string="En producción", compute="_compute_create_prodction")
    product_uom_qty_requisition = fields.Float(string="Cant. a comprar")
    product_uom_qty_requisition_done = fields.Float(string="Cant. comprada")
    product_request_created = fields.Boolean(string="Solicitud de producto Creada", default=False)
    bom_line_ids = fields.One2many('stock.move.bom.line', 'stock_move_id', string="Componentes LdM")
    
    def _compute_create_prodction(self):
        for rec in self:
            if rec.production_day_ids:
                rec.production_create = True
        
    def unlink_production(self):
        data_lines = self.env['production.day.line'].search([('stock_picking_id','=', self.picking_id.id)])
        for line in data_lines:
            line.sudo().unlink()
        self.write({'production_day_ids': [(5,)]})
        return
    
    instruction_line = fields.Char(string="Instrucción")

class StockMoveBomLine(models.Model):
    _name = "stock.move.bom.line"
    _description = "Componentes LdM"

    stock_move_id = fields.Many2one('stock.move', string="Movimiento de Producto")
    product_id = fields.Many2one('product.product', string="Producto")
    product_qty = fields.Float(string="Cantidad")
    uom_category_id = fields.Many2one('uom.category', string="Categoría de la unidad de medida")
    uom_id = fields.Many2one('uom.uom', string="Unidad de medida", domain="[('category_id','=',uom_category_id)]")
    area_id = fields.Many2one('production.area', string="Departamento/Area")
    warehouse_id = fields.Many2one('stock.warehouse', string="Bodega a Solicitar")

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.uom_id = rec.product_id.uom_id.id
