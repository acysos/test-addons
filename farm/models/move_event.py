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

from openerp import models, fields,  _


class MoveEvent(models.Model):
    _name = 'farm.move.event'
    _inherit = {'farm.event': 'AbstractEvent_id'}

    from_location = fields.Many2one(comodel_name='stock.location',
                                    string='Origin', required=True,
                                    domain=[('usage', '=', 'internal'),
                                            ('silo', '=', False), ])
    to_location = fields.Many2one(comodel_name='stock.location',
                                  string='Destination', required=True,
                                  domain=[('usage', '=', 'internal'),
                                          ('silo', '=', False), ])
    quantity = fields.Integer(string='Quantity', required=True,
                              default=1)
    unit_price = fields.Float(string='Unit Price', required=True,
                              digits=(16, 4),
                              help='Unitary cost of Animal or Group for'
                              'analytical accounting.')
    uom = fields.Many2one(comodel_name='product.uom', string='UOM')
    weight = fields.Float(string='Weight', digits=(16, 2))
    move = fields.Many2one(comodel_name='stock.move', string='Stock Move',
                           readonly=True)
    weight_record = fields.Selection(
        string='Weight Record',
        selection=[(None, ''),
                   ('farm.animal.weight', 'Animal Weight'),
                   ('farm.animal.group.weight', 'Group Weight'), ],
        readonly=True)
