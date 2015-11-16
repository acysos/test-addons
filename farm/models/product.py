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


class Template(models.Model):
    _inherit = 'product.template'

    farrowing_price = fields.Float(string='Farrowing Price', digits=(16, 4),
                                   help=('Unitary cost for farrowing events.'
                                         'It\'s only used when the product is'
                                         'a group product of a farm specie.'))
    wearing_price = fields.Float(string='Weaning Price', digits=(16, 4),
                                 help=('Unitary cost for weaning events.'
                                       'It\'s only used when the product is a'
                                       'group product of a farm specie.'))
