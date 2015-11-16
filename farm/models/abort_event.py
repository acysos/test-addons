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


class AbortEvent(models.Model):
    _name = 'farm.abort.event'
    _inherit = {'farm.event.import.mixin': 'ImportedEventMixin_id'}

    female_cycle = fields.Many2one(
        comodel_name='farm.animal.female_cycle', string='Female Cycle')

    @api.one
    def confirm(self):
        if not self.is_compatible():
            raise except_orm(
                'Error',
                "Only females can abort")
        if not self.is_ready():
            raise except_orm(
                'Error',
                "Only pregnat females can abort")
        self.female_cycle = self.animal.current_cycle
        self.animal.update_state()
        self.animal.current_cycle.update_state(self)
        super(AbortEvent, self).confirm()

    def is_compatible(self):
        if self.animal_type == 'female':
            return True
        else:
            return False

    def is_ready(self):
        if self.animal.current_cycle.state == 'pregnat':
            return True
        else:
            return False
