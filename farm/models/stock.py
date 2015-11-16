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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

ANIMAL_TYPE = [(None, 'No animal'), ('male', 'Male)'), ('female', 'Female'),
               ('individual', 'Individual'), ('group', 'Group'), ]


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_done(self):
        super(stock_move, self).action_done()
        customer_location = self.env['stock.location'].search([
                ('usage', '=', 'customer')])
        for line in self:
            if customer_location.id == line.location_dest_id.id:
                lots = []
                for lot in line.quant_ids:
                    lots.append(lot.lot_id.name)
                animals_obj = self.env['farm.animal.group']
                partys = animals_obj.search([('state', '!=', 'sold')])
                sale_animal = []
                for party in partys:
                    for lot in lots:
                        if party.number == lot:
                            sale_animal.append(party)
                if len(sale_animal) > 0:
                    self.sale_group(sale_animal)

    @api.one
    def sale_group(self, groups):
        for group in groups:
            for lot in self.quant_ids:
                if lot.lot_id.name == group.number:
                    if lot.qty == group.quantity:
                        self.totalSale(group, lot.qty)
                    else:
                        raise except_orm(
                            'Error',
                            'Sale cuantity are diferent than group size')

    @api.one
    def totalSale(self, group, qty):
        group.state = 'sold'
        farm_mov_obj = self.env['farm.move.event']
        farm_mov_obj.create({
                    'animal_type': 'group',
                    'specie': group.specie.id,
                    'farm': group.farm.id,
                    'animal_group': group.id,
                    'from_location': group.location.id,
                    'to_location': self.location_dest_id.id,
                    'quantity': qty,
                    'unit_price': 1,
                            })


class Lot(models.Model):
    _inherit = 'stock.production.lot'
    animal_type = fields.Selection(selection=ANIMAL_TYPE)
    animal = fields.One2many(comodel_name='stock.lot_farm.animal',
                             inverse_name='animal', string='Animal')
    animal_group = fields.One2many(comodel_name='stock.lot_farm.animal.group',
                                   inverse_name='animal_group', string='Group')


class LotAnimal(models.Model):
    _name = 'stock.lot_farm.animal'
    _rec_name = 'lot'

    lot = fields.Many2one(comodel_name='stock.production.lot',
                          string='Lot', ondelete='RESTRICT',
                          select=True)
    animal = fields.Many2one(comodel_name='farm.animal', string='Animal',
                             requiered=True, ondelete='RESTRICT', select=True)


class LotAnimalGroup(models.Model):
    _name = 'stock.lot_farm.animal.group'
    _rec_name = 'lot'

    lot = fields.Many2one(comodel_name='stock.production.lot',
                          string='Lot', required=True,
                          ondelete='RESTRICT', select=True)
    animal_group = fields.Many2one(
                        comodel_name='farm.animal.group',
                        string='Animal Group', required=True,
                        ondelete='RESTRICT', select=True)


class Location(models.Model):
    _inherit = 'stock.location'

    holding_number = fields.Char(string='holding number')
    external = fields.Boolean(String='External Farm')
    silo = fields.Boolean(string='Silo', select=True, default=False,
                          help='Indicates that the location is a silo.')
    locations_to_fed = fields.Many2many(
        comodel_name='stock.location.silo_stock.location',
        column1='location', string='Location to fed',
        domain=[('silo', '=', False)],
        help='Indicates the locations the silo feeds. Note that this will '
        'only be a default value.')


class LocationSiloLocation(models.Model):
    _name = 'stock.location.silo_stock.location'

    silo = fields.Many2one(comodel_name='stock.location', string='silo',
                           ondelete='CASCADE', required=True, select=True)
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               ondelete='CASCADE', requiered=True, select=True)


class Foster_location_stock(models.Model):
    _name = 'farm.foster.locations'
    _rec_name = 'location'

    specie = fields.Many2one(comodel_name='farm.specie', string='specie')
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               domain=[('usage', '=', 'transit')])


class Transit_location_stock(models.Model):
    _name = 'farm.transit.locations'
    _rec_name = 'location'

    specie = fields.Many2one(comodel_name='farm.specie', string='specie')
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               domain=[('usage', '=', 'transit')])


class Future_maders_location_stock(models.Model):
    _name = 'farm.future_maders.locations'
    _rec_name = 'location'

    specie = fields.Many2one(comodel_name='farm.specie', string='specie')
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               domain=[('usage', '=', 'transit')])
