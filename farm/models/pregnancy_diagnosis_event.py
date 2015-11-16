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


class PregnancyDiagnosisEvent(models.Model):
    _name = 'farm.pregnancy_diagnosis.event'
    _inherit = {'farm.event': 'AbstractEvent_id'}

    result = fields.Selection([
        ('negative', 'Negative'), ('positive', 'Positive'),
        ('nonconclusive', 'Non conclusive'),
        ('not-pregnant', 'Observed not Pregnant'), ],
                              string='Result',
                              required=True, default='positive')
    female_cycle = fields.Many2one(comodel_name='farm.animal.female_cycle',
                                   string='Female Cycle')

    @api.one
    def confirm(self):
        if not self.is_compatible():
            raise except_orm(
                'Error',
                "Only females can be diagnosed")
        if not self.is_ready():
            raise except_orm(
                'Error',
                "Only mated females can be diagnosed")
        self.female_cycle = self.animal.current_cycle
        self.animal.update_state()
        self.animal.current_cycle.update_state(self)
        super(PregnancyDiagnosisEvent, self).confirm()

    def is_compatible(self):
        if self.animal_type == 'female':
            return True
        else:
            return False

    def is_ready(self):
        if self.animal.current_cycle.state == 'mated':
            return True
        else:
            return False
