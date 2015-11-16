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

EVENT_STATES = [
    ('draft', 'Draft'),
    ('validated', 'Validated'),
    ]


class EventOrder(models.Model):
    _name = 'farm.event.order'
    _order = 'timestamp DESC'

    name = fields.Char(string='Reference', select=True, required=True)
    state = fields.Selection(string='State', selection=EVENT_STATES,
                             default='draft')
    animal_type = fields.Selection([
            ('male', 'Male'),
            ('female', 'Female'),
            ('individual', 'Individual'),
            ('group', 'Group'),
            ], string='Animal Type',
            select=True)
    specie = fields.Many2one(comodel_name='farm.specie', string='Specie',
                             select=True, required=True)
    event_type = fields.Selection([
            ('medication', 'Medications'),
            ('insemination', 'Inseminations'),
            ('pregnancy_diagnosis', 'Pregnancy Diagnosis'),
            ('abort', 'Aborts'),
            ('farrowing', 'Farrowings'),
            ('foster', 'Fosters'),
            ('feed', 'Feed'),
            ('weaning', 'Weanings'),
            ('trasformation_event', 'Trasformation Event'),
            ], string="Event Type", required=True, select=True)
    farm = fields.Many2one(comodel_name='stock.location', string='Farm',
                           required=True,
                           domain=[('usage', '=', 'view'), ])
    timestamp = fields.Datetime(string='Date & Time', requiered=True,
                                default=fields.Datetime.now())
    employee = fields.Many2one(comodel_name='res.users', string='Employee',
                               help='Employee that did the job.')
    medication_events = fields.One2many(comodel_name='farm.medication.event',
                                        inverse_name='job_order',
                                        string='Medication')
    insemination_events = fields.One2many(
        comodel_name='farm.insemination.event', inverse_name='job_order',
        string='Insemination')
    pregnancy_diagnosis_events = fields.One2many(
        comodel_name='farm.pregnancy_diagnosis.event',
        inverse_name='job_order',
        string='Pregnanci Diagnosis')
    abort_events = fields.One2many(comodel_name='farm.abort.event',
                                   inverse_name='job_order',
                                   string='Abort Events')
    farrowing_events = fields.One2many(comodel_name='farm.farrowing.event',
                                       inverse_name='job_order',
                                       string='Farrowings')
    foster_events = fields.One2many(comodel_name='farm.foster.event',
                                    inverse_name='job_order',
                                    string='Fosters')
    weaning_events = fields.One2many(comodel_name='farm.weaning.event',
                                     inverse_name='job_order',
                                     string='weaning')
    feed_events = fields.One2many(comodel_name='farm.feed.event',
                                  inverse_name='job_order',
                                  column1='feed_inventory',
                                  string='feed')
    trasformation_events = fields.One2many(
                    comodel_name='farm.transformation.event',
                    inverse_name='job_order', string='Tasformation Events')
    notes = fields.Text(string='Notes')

    def get_active_events(self):
        if self.event_type == 'medication':
            active_events = self.medication_events
        elif self.event_type == 'insemination':
            active_events = self.insemination_events
        elif self.event_type == 'pregnancy_diagnosis':
            active_events = self.pregnancy_diagnosis_events
        elif self.event_type == 'abort':
            active_events = self.abort_events
        elif self.event_type == 'farrowing':
            active_events = self.farrowing_events
        elif self.event_type == 'foster':
            active_events = self.foster_events
        elif self.event_type == 'feed':
            active_events = self.feed_events
        elif self.event_type == 'weaning':
            active_events = self.weaning_events
        elif self.event_type == 'trasformation_event':
            active_events = self.trasformation_events
        return active_events

    @api.one
    def confirm(self):
        if(self.confirm_event(self.get_active_events())):
                self.state = 'validated'
        else:
            raise except_orm(
                'Error',
                'There are no event associated with this work order')

    def confirm_event(self, event_type):
        events = event_type.search([('state', '=', 'draft'),
                                    ('job_order', '=', self.id)])
        control = False
        for event in events:
            if event.farm.id != self.farm.id:
                raise except_orm(
                    'Error',
                    'The values of farm are diferent on order and events')
            elif self.animal_type:
                if event.animal_type != self.animal_type:
                    raise except_orm(
                        'Error',
                        'The values of animal type are diferent on order'
                        ' and events')
            if event.specie != self.specie:
                raise except_orm(
                    'Error',
                    'The values of specie are diferent on order and events')
            else:
                control = event.confirm()
                if control is None:
                    control = False
        return control
