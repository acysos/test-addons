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


class FeedEventMixin(models.Model):
    _name = 'farm.event.feed_mixin'
    _inherit = {'farm.event': 'AbstractEvent_id'}

    location = fields.Many2one(comodel_name='stock.location',
                               string='Location',
                               domain=[('usage', '=', 'internal'),
                                       ('silo', '=', False), ],
                               required=True)
    quantity = fields.Integer(string='Num. of animals', compute='get_quantity',
                              store=True)
    feed_location = fields.Many2one(comodel_name='stock.location',
                                    string='Feed Source', required=True,
                                    domain=[('usage', '=', 'internal'), ])
    feed_product = fields.Many2one(comodel_name='product.product',
                                   string='Feed')
    feed_lot = fields.Many2one(comodel_name='stock.production.lot',
                               string='Feed Lot', required=True)
    uom = fields.Many2one(comodel_name='product.uom', string='UOM',
                          required=True)
    feed_quantity = fields.Float(string='Comsumed Cuantity', required=True,
                                 digits=(4, 2), default=1)
    start_date = fields.Date(string='Start Date',
                             default=fields.Date.today(),
                             help='Start date of the period in'
                             'which the given quantity of product was'
                             'consumed.')
    end_date = fields.Date(string='End Date', default=fields.Date.today(),
                           help='End date of the period in which the given'
                           'quantity of product was consumed. It is the date'
                           'of event\'s timestamp.')
    move = fields.Many2one(comodel_name='stock.move', string='Stock Move',
                           readonly=True)

    @api.onchange('feed_product')
    def onchange_feed(self):
        self.uom = self.feed_product.product_tmpl_id.uom_id

    @api.onchange('animal')
    def onchange_animal(self):
        self.location = self.animal.location

    @api.onchange('animal_group')
    def onchange_group(self):
        self.location = self.animal_group.location

    @api.one
    def get_quantity(self):
        if self.animal_type == 'group':
            self.quantity = self.animal_group.quantity
        else:
            self.quantity = 1
