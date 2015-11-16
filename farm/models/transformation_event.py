# -*- encoding: utf-8 -*-
##############################################################################
#
#    @authors: Alexander Ezquevo <alexander@acysos.com>
#    Copyright (C) 2015  Acysos S.L.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api,  _
from openerp.exceptions import except_orm


class TransformationEvent(models.Model):
    _name = 'farm.transformation.event'
    _inherit = {'farm.event': 'AbstractEvent_id'}

    from_location = fields.Many2one(comodel_name='stock.location',
                                    string='Origin', required=True)
    to_animal_type = fields.Selection(selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('individual', 'Individual'),
            ('group', 'Group'),
            ], string='Animal Type to Trasform', requiered=True)
    to_location = fields.Many2one(comodel_name='stock.location',
                                  string='Destination', required=True,
                                  domain=[('usage', '=', 'internal'),
                                          ('silo', '=', False), ])
    quantity = fields.Integer(string='Quantity', required=True,
                              default=1)
    to_animal = fields.Many2one(comodel_name='farm.animal',
                                string='Destination Animal',
                                select=True)
    to_animal_group = fields.Many2one(comodel_name='farm.animal.group',
                                      string='Destination Group',
                                      select=True,
                                      help='Select a Destination Group if you'
                                      'want to add the transformed animals to'
                                      'this group. To create a new group leave'
                                      ' it empty.')
    move = fields.Many2one(comodel_name='stock.move',
                           string='Stock Move', readonly=True)

    @api.one
    @api.onchange('animal', 'animal_group')
    def get_from_location(self):
        if self.animal_type == 'group':
            self.from_location = self.animal_group.location
            self.quantity = self.animal_group.quantity
        else:
            self.from_location = self.animal.location

    @api.one
    def confirm(self):
        if not self.is_compatible_trasformation():
            raise except_orm(
                'Error',
                'Destination animal type no compatible')
            return False
        elif not self.is_compatible_quant():
            return False
        elif not self.is_compatible_to_location():
            return False
        if self.animal_type == 'group' and self.to_animal_type == 'group':
            if self.animal_group != self.to_animal_group:
                self.group_to_group()
            else:
                self.move_group()
        elif self.to_animal_type == 'group':
                self.individual_to_group()
        else:
            self.group_to_indvidual()
        super(TransformationEvent, self).confirm()

    def is_compatible_trasformation(self):
        if self.animal_type == 'female' or self.animal_type == 'male':
            if self.to_animal_type == 'male' or \
                    self.to_animal_type == 'female':
                return False
        elif self.animal_type == 'individual':
            if self.to_animal_type == 'individual':
                return False
        return True

    def is_compatible_quant(self):
        if self.to_animal_type == 'individual' or \
            self.animal_type == 'male' or \
                self.animal_type == 'female' or self.to_animal_type != 'group':
            if self.quantity != 1:
                raise except_orm(
                    'Error',
                    'Quantity no compatible')
                return False
        elif self.animal_group.quantity < self.quantity:
            raise except_orm(
                'Error',
                'quantity is biger than group quantity')
            return False
        elif self.quantity < 1:
            raise except_orm(
                'Error',
                'quantity is smaler than one')
            return False
        return True

    def is_compatible_to_location(self):
        if self.animal_type == 'group' and self.to_animal_type == 'group':
            if self.to_animal_group != self.animal_group:
                if self.to_animal_group.location.id != \
                        self.to_location.id:
                    raise except_orm(
                        'Error',
                        'the destination is different from the location of'
                        ' the destination group')
                    return False
        elif self.animal_type != 'group':
            if self.to_animal_group.location.id != \
                        self.to_location.id:
                    raise except_orm(
                        'Error',
                        'the destination is different from the location of'
                        ' the destination group')
        elif self.animal_group.location == self.to_location:
            raise except_orm(
                        'Error',
                        'the destination of animal is the same of the location'
                        'of the origin group')
        return True

    @api.one
    def group_to_group(self):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        production_lot_obj = self.env['stock.production.lot']
        animal_group_lot_obj = self.env['stock.lot_farm.animal.group']
        lots = []
        for lot in self.to_animal_group.lot:
            lots.append(lot.id)
        for lot in self.animal_group.lot:
            product_id = self.animal_group.lot.lot.product_id.id
            product_uom = \
                self.animal_group.lot.lot.product_id.product_tmpl_id.uom_id.id
            initial_location = self.animal_group.location.id
            lot_id = lot.lot.id
            duplicate_lot = animal_group_lot_obj.create({
                        'animal_group': self.to_animal_group.id,
                        'lot': lot.lot.id})
            lots.append(duplicate_lot.id)
        self.to_animal_group.initial_quantity += self.quantity
        self.to_animal_group.quantity += self.quantity
        target_quant = quants_obj.search([
                ('lot_id', '=', lot_id),
                ('location_id', '=', initial_location),
                ])
        if len(self.to_animal_group.lot) < 3:
            new_lot = production_lot_obj.create({
                    'product_id': product_id,
                    'animal_type': 'group',
                    })
            new_animal_group_lot = animal_group_lot_obj.create({
                'lot': new_lot.id,
                'animal_group': self.to_animal_group.id})
            lots.append(new_animal_group_lot.id)
        else:
            new_lot = self.to_animal_group.lot[2]
        self.to_animal_group.lot = lots
        new_move = moves_obj.create({
            'name': 'regroup-' + new_lot.name,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': product_id,
            'product_uom_qty': self.quantity,
            'product_uom': product_uom,
            'location_id': initial_location,
            'location_dest_id': self.to_animal_group.location.id,
            'company_id': self.to_animal_group.initial_location.company_id.id,
            'origin': self.job_order.name
            })
        for q in target_quant:
            q.reservation_id = new_move.id
        new_move.action_done()
        old_quants = []
        for lot in self.to_animal_group.lot:
            old_quants.append(quants_obj.search([
                ('lot_id', '=', lot.lot.id),
                ('location_id', '=', self.to_animal_group.location.id)
                ]))
        for quant in new_move.quant_ids:
            quant.lot_id = new_lot
        for qs in old_quants:
            for q in qs:
                q.lot_id = new_lot
        if self.animal_group.quantity > self.quantity:
            self.animal_group.quantity -= self.quantity
            self.animal_group.initial_quantity -= self.quantity
        else:
            for line in self.animal_group.account.line_ids:
                line.account_id = self.to_aniimal_group.account
                line.name = line.name + '-Regroup-' + self.animal_group.number
            self.animal_group.active = False
        self.move = new_move
        transition_location = []
        for loc in self.specie.lost_found_location:
            transition_location.append(loc.id)
        if self.to_location.id not in transition_location:
            self.animal_group.state = 'fatten'

    def get_farm(self, location):
        while(location.location_id.id != 1):
            location = location.location_id
        return location
    @api.one
    def group_to_indvidual(self):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        production_lot_obj = self.env['stock.production.lot']
        animal_obj = self.env['farm.animal']
        animal_lot_obj = self.env['stock.lot_farm.animal']
        self.animal_group.quantity -= 1
        if len(self.animal_group.lot) > 1:
            lot = self.animal_group.lot[2].lot
        else:
            lot = self.animal_group.lot.lot
        target_quant = quants_obj.search([
                ('lot_id', '=', lot.id),
                ('location_id', '=', self.animal_group.location.id),
                ])
        product_uom = \
            lot.product_id.product_tmpl_id.uom_id.id
        new_move = moves_obj.create({
            'name':
                'separation-' + self.to_animal_type + '-' +
                lot.name,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': lot.product_id.id,
            'product_uom_qty': 1,
            'product_uom': product_uom,
            'location_id': self.animal_group.location.id,
            'location_dest_id': self.to_location.id,
            'company_id': self.animal_group.initial_location.company_id.id,
            'origin': self.job_order.name
            })
        for q in target_quant:
            q.reservation_id = new_move.id
        new_move.action_done()
        animal = quants_obj.search([
            ('lot_id', '=', lot.id),
            ('location_id', '=', self.to_location.id)])
        if self.to_animal_type == 'female':
            animal.product_id = self.animal_group.specie.female_product.id
        elif self.to_animal_type == 'male':
            animal.product_id = self.animal_group.specie.male_product.id
        else:
            animal.product_id = self.animal_group.specie.individual_product.id
        new_lot = production_lot_obj.create({
                    'product_id': animal.product_id.id
                    })
        animal.lot_id = new_lot
        self.move = new_move
        sex = {'male': 'male',
               'female': 'female',
               'individual': 'undetermined',
               }
        new_animal = animal_obj.create({
            'type': self.to_animal_type,
            'specie': self.animal_group.specie.id,
            'breed': self.animal_group.breed.id,
            'farm': self.get_farm(self.to_location).id,
            'origin': 'purchased',
            'birthdate': self.animal_group.arrival_date,
            'initial_location': self.to_location.id,
            'sex': sex[self.to_animal_type],
            })
        animal_lot_obj.create({
                'animal': new_animal.id,
                'lot': new_lot.id})
        new_animal.origin = 'raised'
        self.to_animal = new_animal

    @api.one
    def move_group(self):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        if len(self.animal_group.lot) > 1:
            lot_id = self.animal_group.lot[2].lot.id
        else:
            lot_id = self.animal_group.lot[0].lot.id
        print 'dos'
        target_quant = quants_obj.search([
                ('lot_id', '=', lot_id),
                ('location_id', '=', self.animal_group.location.id),
                ])
        m_g_move = moves_obj.create({
            'name': 'relocation-' + self.animal_group.number,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': self.animal_group.lot.lot.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom':
                self.animal_group.lot.lot.product_id.product_tmpl_id.uom_id.id,
            'location_id': self.animal_group.location.id,
            'location_dest_id': self.to_location.id,
            'company_id': self.animal_group.farm.company_id.id, })
        for q in target_quant:
            q.reservation_id = m_g_move.id
        print 'tres'
        m_g_move.action_done()
        self.move = m_g_move
        self.animal_group.location = self.to_location
        self.animal_group.farm = self.get_farm(self.to_location)
        transition_location = []
        for loc in self.specie.lost_found_location:
            transition_location.append(loc.id)
        if self.to_location.id not in transition_location:
            self.animal_group.state = 'fatten'

    @api.one
    def individual_to_group(self):
        moves_obj = self.env['stock.move']
        quants_obj = self.env['stock.quant']
        production_lot_obj = self.env['stock.production.lot']
        animal_group_lot_obj = self.env['stock.lot_farm.animal.group']
        lots = []
        for lot in self.to_animal_group.lot:
            lots.append(lot.id)
        product_id = self.animal.lot.lot.product_id.id
        product_uom = \
            self.animal.lot.lot.product_id.product_tmpl_id.uom_id.id
        initial_location = self.animal.location.id
        lot_id = self.animal.lot.lot.id
        self.to_animal_group.initial_quantity += self.quantity
        self.to_animal_group.quantity += self.quantity
        target_quant = quants_obj.search([
                ('lot_id', '=', lot_id),
                ('location_id', '=', initial_location),
                ])
        if len(self.to_animal_group.lot) < 3:
            new_lot = production_lot_obj.create({
                    'product_id': product_id
                    })
        else:
            new_lot = self.to_animal_group.lot[2]
        new_animal_group_lot = animal_group_lot_obj.create({
            'lot': new_lot.id,
            'animal_group': self.to_animal_group.id})
        lots.append(new_animal_group_lot.id)
        self.to_animal_group.lot = lots
        new_move = moves_obj.create({
            'name': 'regroup-' + new_lot.name,
            'create_date': fields.Date.today(),
            'date': self.timestamp,
            'product_id': product_id,
            'product_uom_qty': self.quantity,
            'product_uom': product_uom,
            'location_id': initial_location,
            'location_dest_id': self.to_animal_group.location.id,
            'company_id': self.to_animal_group.initial_location.company_id.id,
            'origin': self.job_order.name,
            })
        for q in target_quant:
            q.reservation_id = new_move.id
        new_move.action_done()
        old_quants = []
        for lot in self.to_animal_group.lot:
            old_quants.append(quants_obj.search([
                ('lot_id', '=', lot.lot.id),
                ('location_id', '=', self.to_animal_group.location.id)
                ]))
        for move in new_move:
            move.quant_ids.lot_id = new_lot
        for qs in old_quants:
            for q in qs:
                q.lot_id = new_lot
        self.animal.active = False
        animal = self.env['stock.quant'].search([
            ('lot_id', '=', new_lot.id),
            ('product_id', '=', product_id),
            ])
        animal.product_id = self.to_animal_group.lot[0].lot.product_id
        self.move = new_move
