# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import date, datetime
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    in_production = fields.Boolean(string="En producción", compute="_compute_in_production")
    production_area_check = fields.Boolean(string="Áreas de Producción", related="picking_type_id.production_area_check")
    name_extern = fields.Char(string="OT externo")

    purchase_requisition = fields.Boolean(string="Check Purchase", related="picking_type_id.purchase_requisition")
    purchase_requisition_id = fields.Many2one('purchase.requisition', string="Acuerdo de compra")
    user_requisition = fields.Char(string="Solicitante(s)")
    department_requisition = fields.Char(string="Departamento")
    product_request_state = fields.Selection([('draft','Sin solicitar a Bodega'),('done','Solicitado a Bodega'),('send','Entregado')], string='Solicitud Bodega')
    date_product_request = fields.Datetime(string="Fecha Solicitud de Producto")
    date_product_request_done = fields.Datetime(string="Fecha Entrega de Solicitud de Producto")
    stock_picking_product_request = fields.Boolean(string="Solicitud de Materia Prima", default=False)
    origin_stock_picking_id = fields.Many2one('stock.picking', string="Origen de Solicitud de Material")
    count_product_request_stock_picking = fields.Integer(string="Solicitudes de Material", compute='_computed_count_product_request')
    stock_picking_type_product_request = fields.Boolean(string='Albaran para Solicitar Materiales', compute='_computed_type_picking_product_request')
    product_request_warehouse = fields.Boolean(string='Albaran de Solicitud de Materiales', compute='_computed_type_picking_product_request')
    area_product_request_id = fields.Many2one('production.area', string="Area Solicitada")
    actual_production_area_id = fields.Many2one('production.area', string="Area de Producción Actual", track_visibility='always')
    actual_user_production_area_id = fields.Many2many('res.users', string="Usuario de Producción Actual", track_visibility='always')
    count_point_quality_control = fields.Integer(string="Cantidad de Controles de calidad", compute='_computed_count_point_quality_control')
    point_quality_control = fields.Many2one('point.quality.control', string="Vale de Error o Garantia", track_visibility='always')
    quality_control_check = fields.Boolean(string="Se genera Punto de control", compute='_compute_quality_control_check')
    stage_production_ids = fields.One2many('stage.production', 'stock_picking_id', string='Etapas de producción', track_visibility='always')
    production_stock_picking_active = fields.Boolean(string='Producción Activa', compute='_compute_production_stock_picking_active')

    def _compute_production_stock_picking_active(self):
        for rec in self:
            active = False
            for stage in rec.stage_production_ids:
                if stage.user_id == self.env.user and not stage.date_end:
                    active = True
            rec.production_stock_picking_active = active

    def set_date_start_stage_production(self):
        for rec in self:
            if not self.env.user.production_area_id:
                raise UserError('Su usuario no tiene establecida un area de Producción, favor solicitar que le establezcan una en su usuario')
            for line in rec.stage_production_ids:
                if line.user_id == self.env.user and not line.date_end:
                    raise UserError("Usted tiene un ingreso activo en este albaran, cierrelo antes de ingresar nuevamente.")
            line_stage = self.env['stage.production'].create({'user_id':self.env.user.id,
                                                              'date_start':datetime.now(),
                                                              'production_area_id':self.env.user.production_area_id.id, 
                                                              'stock_picking_id':rec.id})
            print(rec.actual_user_production_area_id)
            rec.write({'actual_production_area_id': self.env.user.production_area_id.id,
                       'actual_user_production_area_id':[(4, self.env.user.id)]})
            print(rec.actual_user_production_area_id)

    def set_date_end_stage_production(self):
        for rec in self:
            for line in rec.stage_production_ids:
                if line.user_id == self.env.user and not line.date_end:
                    line.write({'date_end':datetime.now()})
            rec.write({'actual_production_area_id': False,
                       'actual_user_production_area_id':[(3, self.env.user.id)]})

    @api.one
    def _compute_quality_control_check(self):
        for rec in self:
            rec.quality_control_check = rec.picking_type_id.quality_control

    @api.one
    def _computed_type_picking_product_request(self):
        for rec in self:
            rec.stock_picking_type_product_request = rec.picking_type_id.stock_picking_type_product_request
            rec.product_request_warehouse = rec.picking_type_id.product_request_warehouse
            if rec.count_product_request_stock_picking > 0:
                rec.stock_picking_type_product_request = False
            if rec.state != 'assigned':
                rec.stock_picking_type_product_request = False

    @api.one
    def _computed_count_product_request(self):
        for rec in self:
            name_picking = rec.name
            base_product_request = self.env['stock.picking'].search([('name','=',name_picking)])
            product_request = self.env['stock.picking'].search([('origin_stock_picking_id','=',base_product_request.id)])
            rec.count_product_request_stock_picking = len(product_request)

    @api.multi
    def action_view_product_request_related(self):
        product_request = self.env['stock.picking'].search([('origin_stock_picking_id','=',self.id)])
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', product_request.ids]],
            "name": "Solicitud relacionada",
        }

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if res.picking_type_id.product_request_warehouse:
            res.write({'product_request_state':'draft'})
        if res.origin:
            sale_id = self.env['sale.order'].sudo().search([('name','=',res.origin)])
            if sale_id:
                line_stage = self.env['stage.production'].create({'user_id':sale_id.user_id.id,
                                    'date_start':datetime.now(),
                                    'production_area_id':sale_id.user_id.production_area_id.id, 
                                    'stock_picking_id':res.id})
        return res

    def action_assign(self):
        res = super(StockPicking, self).action_assign()
        for rec in self:
            if rec.state == 'assigned':
                if rec.origin:
                    sale_id = self.env['sale.order'].sudo().search([('name','=',rec.origin)])
                    if sale_id:
                        for line in rec.stage_production_ids:
                            if line.user_id == sale_id.user_id and not line.date_end:
                                line.write({'date_end':datetime.now()})

    def action_product_request_done(self):
        for rec in self:
            rec.write({'product_request_state':'send','date_product_request_done':datetime.now()})
            return

    def print_production_request(self):
        return self.env.ref('gp_stock.gp_stock_picking_product_request').report_action(self)

    def create_product_request(self):
        for rec in self:
            """Se verificaran las líneas del alabarán y abrira una ventana para establecer la cantidad
            y componentes para crear las solicitudes de materia prima."""
            product_without_componentes = False
            for line_move in rec.move_ids_without_package:
                if not line_move.product_id.bom_ids and not line_move.bom_line_ids:
                    product_without_componentes = True
            if product_without_componentes == True:
                self.ensure_one()
                ir_model_data = self.env['ir.model.data']
                compose_form_id = ir_model_data.get_object_reference('gp_stock', 'view_stock_move_product_request')[1]
                ctx = {
                    'default_line_ids': rec.move_ids_without_package.filtered(lambda l : not l.product_id.bom_ids).ids,
                }
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.move.product.request',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'target': 'new',
                    'context': ctx,
                }
            """Se verifican las areas y bodegas a las cuales se tiene que solicitar el producto de
            materia prima de aquellos productos que tienen lista de materiales. La logica sera la siguiente:
            1. Agrupara en un diccionario los componentes de los productos vendidos guardando su area y bodega
            2. Verificara en el diccionario de albaranes si existe uno con la bodega y area, si existe,
                creara una línea de albaran en el albaran correspondiente.
            3. Si no existe un albaran con el area y bodega del componente, creara un albaran y lo guardara
                en el diccionario de albaranes, luego creara la línea de albaran relacionando el nuevo albaran."""
            picking_product_request_ids = []
            area_ids = self.env['production.area'].sudo().search([])
            warehouse_ids = self.env['stock.warehouse'].sudo().search([])
            for warehouse in warehouse_ids:
                for area in area_ids:
                    line_ids = []
                    for line_picking in rec.move_ids_without_package:
                        if line_picking.product_id.bom_ids and line_picking.product_request_created == False:
                            for bom in line_picking.product_id.bom_ids:
                                for bom_line in bom.bom_line_ids:
                                    if bom_line.area_id.id == area.id and bom_line.warehouse_id.id == warehouse.id:
                                        vals = {'product_id': bom_line.product_id.id,
                                            'product_uom_qty': bom_line.product_qty*line_picking.product_uom_qty,
                                            'product_uom_id': bom_line.product_uom_id.id,
                                            'area':area.id,
                                            'warehouse':warehouse.id}
                                        line_ids.append(vals)
                    for line_without_bom in rec.move_ids_without_package.filtered(lambda l : not l.product_id.bom_ids):
                        for component in line_without_bom.bom_line_ids:
                            if component.area_id.id == area.id and component.warehouse_id.id == warehouse.id:
                                vals = {'product_id':component.product_id.id,
                                        'product_uom_qty':component.product_qty,
                                        'product_uom_id':component.uom_id.id,
                                        'area':area.id,
                                        'warehouse':warehouse.id}
                                line_ids.append(vals)
                    if len(line_ids) > 0:
                        for line in line_ids:
                            picking_product_request_id = False
                            if len(picking_product_request_ids) > 0:
                                for request in picking_product_request_ids:
                                    if line['area'] == request['area'] and line['warehouse'] == request['warehouse']:
                                        picking_product_request_id = request['stock_picking']
                                if picking_product_request_id == False:
                                    vals_stock_picking = {'picking_type_id':warehouse.picking_type_product_request_id.id,
                                        'scheduled_date': datetime.now(),
                                        'origin':self.origin,
                                        'product_request_state':'draft',
                                        'origin_stock_picking_id': self.id,
                                        'location_id': warehouse.picking_type_product_request_id.default_location_src_id.id,
                                        'location_dest_id': warehouse.picking_type_product_request_id.default_location_dest_id.id,
                                        'area_product_request_id':area.id}
                                    picking_product_request_id = self.env['stock.picking'].create(vals_stock_picking)
                                    picking_product_request_id = picking_product_request_id.id
                                    picking_product_request_ids.append({'area':area.id, 'warehouse':warehouse.id,'stock_picking':picking_product_request_id})
                            else:
                                vals_stock_picking = {'picking_type_id':warehouse.picking_type_product_request_id.id,
                                    'scheduled_date': datetime.now(),
                                    'origin':self.origin,
                                    'product_request_state':'draft',
                                    'origin_stock_picking_id': self.id,
                                    'location_id': warehouse.picking_type_product_request_id.default_location_src_id.id,
                                    'location_dest_id': warehouse.picking_type_product_request_id.default_location_dest_id.id,
                                    'area_product_request_id':area.id}
                                picking_product_request_id = self.env['stock.picking'].create(vals_stock_picking)
                                picking_product_request_id = picking_product_request_id.id
                                picking_product_request_ids.append({'area':area.id, 'warehouse':warehouse.id,'stock_picking':picking_product_request_id})
                            picking_product_request_id = self.env['stock.picking'].search([('id','=',picking_product_request_id)])
                            vals_line = {'name':'Solicitud de producto',
                                'picking_id': picking_product_request_id.id,
                                'product_id': line['product_id'],
                                'product_uom_qty': line['product_uom_qty'],
                                'product_uom': line['product_uom_id'],
                                'location_id': picking_product_request_id.location_id.id,
                                'location_dest_id': picking_product_request_id.location_dest_id.id,
                                'state':'draft',
                                'is_locked':False,
                                'scrapped':False,
                                'reference':picking_product_request_id.name,}
                            self.env['stock.move'].create(vals_line)
                        picking_product_request_id.action_confirm()
            for line_stock in rec.move_ids_without_package:
                line_stock.write({'product_request_created':True})
        return

    def action_product_request_warehouse(self):
        for rec in self:
            rec.write({'product_request_state':'done','date_product_request':datetime.now()})
            return self.env.ref('gp_stock.gp_stock_picking_product_request').report_action(self)

    def _compute_in_production(self):
        for rec in self:
            id_days = []
            id_area = []
            create_line = True
            for line in self.move_ids_without_package:
                if line.product_id.type != 'service':
                    for production_area in line.production_area_ids:
                        if production_area.id not in id_area:
                            id_area.append(production_area.id)
                        if line.production_day_ids:
                            for production_day in line.production_day_ids:
                                if  production_day.production_area_id.id not in id_days:
                                    id_days.append(production_day.production_area_id.id)
            if len(id_area) == len(id_days):
                create_line = False
            if create_line == True:
                rec.in_production = False
            else:
                rec.in_production = True

    def action_production_in(self):
        for line in self.move_ids_without_package:
            if line.product_id.type != 'service':
                for production_area in line.production_area_ids:
                    create_line = True
                    if line.production_day_ids:
                        for production_day in line.production_day_ids:
                            if  production_day.production_area_id.id == production_area.id:
                                create_line = False 
                    else:
                        create_line = True
                    if create_line == True:
                        production_day_id = self.env['production.day'].search([('production_area_id','=',production_area.id),('next_production_id','=', False)], limit=1)
                        if production_day_id:
                            vals = {
                                    'name': 'line',
                                    'production_day': production_day_id.id,
                                    'stock_picking_id': self.id,
                                    'origin_id': self.origin,
                                    'product_id': line.product_id.id,
                                    'product_qty': line.product_qty,
                                    'production_area_id': production_area.id,
                                    'date_in': datetime.datetime.today(),
                                }
                            self.env['production.day.line'].create(vals)
                            line.write({'production_day_ids': [(4, production_day_id.id)]})
        return
    
    def create_purchase_requisition(self):
        create_requisition = False
        for line in self.move_ids_without_package:
            if line.product_uom_qty_requisition != 0 and line.product_uom_qty_requisition_done != line.product_uom_qty_requisition:
                create_requisition = True
                if self.purchase_requisition_id:
                    if self.name not in self.purchase_requisition_id.origin:
                        self.purchase_requisition_id.write({'origin': self.purchase_requisition_id.origin + ', ' + self.name})
                    vals_line = {
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'product_qty': line.product_uom_qty_requisition,
                        'requisition_id': self.purchase_requisition_id.id,
                    }
                    self.env['purchase.requisition.line'].create(vals_line)
                    line.write({'product_uom_qty_requisition_done': line.product_uom_qty_requisition})
                    if line.instruction_line:
                        if self.purchase_requisition_id.description:
                            self.purchase_requisition_id.write({'description': line.instruction_line + ', \n' + self.purchase_requisition_id.description})
                        else:
                            self.purchase_requisition_id.write({'description': line.instruction_line})
                    if self.user_requisition:
                        if self.purchase_requisition_id.user_requisition:
                            self.purchase_requisition_id.write({'user_requisition': str(self.user_requisition) + ', ' + str(self.purchase_requisition_id.user_requisition)})
                        else:
                            self.purchase_requisition_id.write({'user_requisition': self.user_requisition})
                else:
                    vals = {
                        'origin': self.name,
                        'date_end': date.today(),
                        'ordering_date': date.today(),
                        'schedule_date': date.today(),
                    }
                    requisition = self.env['purchase.requisition'].create(vals)
                    self.write({'purchase_requisition_id': requisition.id})
                    vals_line = {
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'product_qty': line.product_uom_qty_requisition,
                        'requisition_id': requisition.id,
                    }
                    self.env['purchase.requisition.line'].create(vals_line)
                    line.write({'product_uom_qty_requisition_done': line.product_uom_qty_requisition})
                    if line.instruction_line:
                        if self.purchase_requisition_id.description:
                            self.purchase_requisition_id.write({'description': line.instruction_line + ', \n' + self.purchase_requisition_id.description})
                        else:
                            self.purchase_requisition_id.write({'description': line.instruction_line})
                    if self.user_requisition:
                        if self.purchase_requisition_id.user_requisition:
                            self.purchase_requisition_id.write({'user_requisition': str(self.user_requisition) + ', ' + str(self.purchase_requisition_id.user_requisition)})
                        else:
                            self.purchase_requisition_id.write({'user_requisition': self.user_requisition})
                    requisition.action_in_progress()
        if create_requisition == False:
            raise UserError('No hay líneas para crear acuerdo de compra')
        return

    def action_quality_control_test(self):
        lines =[]
        for warehouse_picking_type_id in self.picking_type_id.warehouse_id.quality_control_test.filtered(lambda r: r.production_area_id == self.actual_production_area_id):
            lines.append((0,0,{'name':warehouse_picking_type_id.name, 
                        'production_area_id':warehouse_picking_type_id.production_area_id.id,
                        'control_quality':False}))
        for question_picking_type_id in self.picking_type_id.quality_control_test.filtered(lambda r: r.production_area_id == self.actual_production_area_id):
            lines.append((0,0,{'name':question_picking_type_id.name, 
                        'production_area_id':question_picking_type_id.production_area_id.id,
                        'control_quality':False}))
        #ALERTA!!!!!
        #Hace falta la programación de Categorias y Productos

        product_ids = []
        for line in self.move_ids_without_package:
            if line.product_id.id not in product_ids:
                product_ids.append(line.product_id.id)
        detail_product = []
        for product in product_ids:
            qty_product = 0
            for line in self.move_ids_without_package:
                if product == line.product_id.id:
                    qty_product += line.product_uom_qty
            detail_product.append((0,0,{'name':'name','product_id':product,'qty':qty_product}))
        ctx = {'default_stock_picking_id': self.id,
               'default_date_start': datetime.now(),
               'default_user_id': self.env.user.id,
               'default_production_area_id':self.actual_production_area_id.id,
               'default_question_line_ids':lines,
               'default_product_line_ids':detail_product,
               }
        return {
            'name': ('Punto de Control'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'quality.control.request',
            'context': ctx,
        }

    @api.one
    def _computed_count_point_quality_control(self):
        for rec in self:
            rec.count_point_quality_control = len(self.env['point.quality.control'].sudo().search([('stock_picking_id','=',rec.id)]))

    @api.multi
    def action_view_quality_control(self):
        point_quality_control = self.env['point.quality.control'].sudo().search([('stock_picking_id','=',self.id)])
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "point.quality.control",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', point_quality_control.ids]],
            "name": "Puntos de Control de Calidad",
        }

class StageProduction(models.Model):
    _name = 'stage.production'
    _description = 'Estados de Producción'

    name = fields.Char('Etapa')
    date_start = fields.Datetime(string="Ingreso")
    date_end = fields.Datetime(string="Salida")
    user_id = fields.Many2one('res.users', string="Usuario")
    production_area_id = fields.Many2one('production.area', string="Area")
    stock_picking_id = fields.Many2one('stock.picking', string='Albaran')
    time = fields.Float(string="Tiempo usado", compute='_compute_time')

    @api.one
    def _compute_time(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                difference_time = rec.date_end - rec.date_start
                seconds = difference_time.seconds
                days = difference_time.days
                minutes = ((seconds/60)%60)/60.0
                hours = seconds/3600
                days = days * 24
                rec.time = hours + minutes + days