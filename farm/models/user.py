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


class User(models.Model):
    _inherit = 'res.users'

    farm = fields.Many2many(comodel_name='res.user_stock.location',
                            inverse_name='user', colum1='location',
                            string='Farms',
                            domain=[('type', '=', 'warehouse'), ],
                            help="Farms to which this user is assigned."
                            "Determine animals that he/she can manage.")


class UserLocation(models.Model):
    _name = 'res.user_stock.location'

    user = fields.Many2one(comodel_name='res.users', string='User',
                           ondelete='CASCADE', required=True, select=True)
    location = fields.Many2one(comodel_name='stock.location',
                               string='Location', ondelete='CASCADE',
                               required=True, select=True)
