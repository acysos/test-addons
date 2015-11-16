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


class FeedEvent(models.Model):
    _name = 'farm.feed.event'
    _inherit = {'farm.event.feed_mixin': 'FeedEventMixin_id'}

    animal_type = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),
        ('individual', 'Individual'), ('group', 'Group'),
        ], string="Animal Type", select=True)
    feed_quantity_animal_day = fields.Float(string='Qty. per Animal Day',
                                            digits=(16, 4), readonly=True)
    feed_inventory = fields.Many2one(comodel_name='farm.feed.inventory',
                                     string='Inventory')
    feed_inventory = fields.Selection(string='Inventory',
                                      selection='get_inventory',
                                      readonly=True, select=True,
                                      help='The inventory that generated this'
                                      'event automatically.')

    @api.one
    def confirm(self):
        quants_obj = self.env['stock.quant']
        moves_obj = self.env['stock.move']
        target_quant = quants_obj.search([
            ('lot_id', '=', self.feed_lot.id),
            ('location_id', '=', self.feed_location.id)])
        new_move = moves_obj.create({
            'name': self.job_order.name+'-'+self.lot.name+'-mov',
            'create_date': fields.Date.today(),
            'date': self.start_date,
            'product_id': self.feed_product.id,
            'product_uom_qty': self.feed_quantity,
            'product_uom': self.uom.id,
            'location_id': self.feed_location.id,
            'location_dest_id': self.location.id,
            'company_id': self.location.company_id.id,
            'origin': self.job_order.name,
            })
        for q in target_quant:
            q.reservation_id = new_move.id
        new_move.action_done()
        if self.animal_type == 'group':
            self.animal_group.feed_quantity += self.feed_quantity
            self.set_cost(
                self.animal_group.account, self.feed_lot, self.feed_quantity)
        else:
            self.animal.consumed_feed += self.feed_quantity
            self.set_cost(
                self.animal.account, self.feed_lot, self.feed_quantity)
        consumed_quants = quants_obj.search([
            ('lot_id', '=', self.feed_lot.id),
            ('location_id', '=', self.location.id)])
        if not consumed_quants:
            consumed_quants = quants_obj.search([
                ('location_id', '=', self.location.id)])
        consumed_feed = self.feed_quantity
        for q in consumed_quants:
            if q.qty >= consumed_feed:
                q.qty -= consumed_feed
                consumed_feed = 0
                if q.qty == 0:
                    q.unlink()
            else:
                consumed_feed -= q.qty
                q.qty = 0
                q.unlink()
        super(FeedEvent, self).confirm()

    @api.one
    def set_cost(self, account, lot, qty):
        company = self.env['res.company'].search([
                        ('id', '=', self.farm.company_id.id)])
        journal = self.env['account.analytic.journal'].search([
                                ('code', '=', 'FAR')])
        analytic_line_obj = self.env['account.analytic.line']
        if lot.unit_cost:
            cost = lot.unit_cost * qty
        else:
            quants_obj = self.env['stock.quant']
            quants = quants_obj.search([
                    ('lot_id', '=', self.feed_lot.id),
                    ('location_id', '=', self.location.id)])
            if len(quants) < 1:
                quants = quants_obj.search([
                            ('location_id', '=', self.location.id)])
            cost = quants[0].cost * qty
        analytic_line_obj.create({
                    'name': self.job_order.name,
                    'date': self.end_date,
                    'amount': -(cost),
                    'unit_amount': qty,
                    'account_id': account.id,
                    'general_account_id': company.feed_account.id,
                    'journal_id': journal.id,
                    })

    def get_inventory(self):
        irModel_obj = self.env['ir.model']
        models = irModel_obj.search([
                ('model', 'in', ['farm.feed.inventory',
                                 'farm.feed.provisional_inventory']),
                ])
        return [('', '')] + [(m.model, m.name) for m in models]
