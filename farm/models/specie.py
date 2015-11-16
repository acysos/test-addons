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


class Specie(models.Model):
    _name = 'farm.specie'

    name = fields.Char(string='name', traslate=True, required=True,
                       help='Name of the specie. ie. "Pig"')
    male_product = fields.Many2one(
            comodel_name='product.product', string="Male's Product")
    male_enabled = fields.Boolean(
        string='Males Enabled',
        default=True,
        help="If checked the menus to manage this kind of animal"
        "will be generated. If you don't want "
        "it, uncheck and put a generic product or other type of animal "
        "because it is required.")
    female_product = fields.Many2one(
        comodel_name='product.product',
        string="Female's Product",
        # domain=[('uom_id.category_id.name', '=', 'Unit')]
        )
    female_enabled = fields.Boolean(
        string='Females Enabled',
        default=True,
        help="If checked the menus to manage this kind of animal will be"
        "generated. If you don't want it, uncheck and put a generic product or"
        " other type of animal because it is required.")
    individual_product = fields.Many2one(
        comodel_name='product.product',
        string="Individual's Product",
        # domain=[('uom_id.category_id.name', '=', 'Unit')]
        )
    individual_enabled = fields.Boolean(
        string='Individuals Enabled', default=True,
        help="If checked the menus to manage this kind of animal will be"
        "generated. If you don't want it, uncheck and put a generic product or"
        "other type of animal because it is required.")
    group_product = fields.Many2one(
        comodel_name='product.product', string="Group's Product")
    group_enabled = fields.Boolean(
        string='Groups Enabled', default=True,
        help="If checked the menus to manage this kind of animal"
        "will be generated. If you don't want it, uncheck and put a generic"
        " product or other type of animal because it is required.")
    semen_product = fields.Many2one(
        comodel_name='product.product', string="Semen's Product",
        help="Product for the mixture of semen to raise the expected "
        "quality.\nIt is used in the Production lots produced in the "
        "Extraction Events and in the BoM containers for doses used in "
        "deliveries to farms for inseminations.")
    breeds = fields.One2many(comodel_name='farm.specie.breed',
                             inverse_name='specie', string='Breeds')
    farm_lines = fields.One2many(comodel_name='farm.specie.farm_line',
                                 inverse_name='specie', string='Farms')
    removed_location = fields.Many2one(
        comodel_name='stock.location', string='Removed Location',
        domain=[('usage', '=', 'transit')],
        required=True,
        help='Virtual location where removed animals are moved to.')
    foster_location = fields.One2many(
        comodel_name='farm.foster.locations', inverse_name='specie',
        string='Foster Location',
        required=True,
        help='Virtual location where fostered animals are moved to.')
    lost_found_location = fields.One2many(
        comodel_name='farm.transit.locations', inverse_name='specie',
        string='Transit Location',
        required=True,
        help='Virtual location where lost or found animals are moved to.')
    future_maders_location = fields.One2many(
        comodel_name='farm.future_maders.locations', inverse_name='specie',
        string='Future maders location',
        required=True)
    feed_lost_found_location = fields.Many2one(
        comodel_name='stock.location', inverse_name='specie',
        string='Feed transit',
        domain=[('usage', '=', 'transit')],
        required=True)

    @api.onchange('male_enabled')
    def onChange_male_enabled(self):
        if self.male_enabled is False:
            self.male_product = False

    @api.onchange('female_enabled')
    def onChange_female_enabled(self):
        if self.female_enabled is False:
            self.female_product = False

    @api.onchange('individual_enabled')
    def onChange_individual_enabled(self):
        if self.individual_enabled is False:
            self.individual_product = False

    @api.onchange('individual_enabled')
    def onChange_group_enabled(self):
        if self.group_enabled is False:
            self.group_product = False


class Breed(models.Model):
    'Breed of Specie'
    _name = 'farm.specie.breed'

    specie = fields.Many2one(comodel_name='farm.specie',
                             string='Specie', required=True,
                             ondelete='CASCADE')
    name = fields.Char(string='Name', required=True)


class SpecieFarmLine(models.Model):
    'Managed Farm of specie'
    _name = 'farm.specie.farm_line'

    specie = fields.Many2one(comodel_name='farm.specie',
                             string='Specie', required=True,
                             ondelete='CASCADE')
    farm = fields.Many2one(comodel_name='stock.location',
                           string='Farm', required=True,
                           domain=[('usage', '=', 'view')])
    event_order_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Events Orders' Sequence", required=True, domain=[
            ('code', '=', 'farm.event.order')
            ],
        help="Sequence used for the Event Orders in this farm.")
    has_male = fields.Boolean(string='Males',
                              help="In this farm there are males.")
    male_sequence = fields.Many2one(
        comodel_name='ir.sequence', string="Males' Sequence",
        domain=[('code', '=', 'farm.animal')],
        help='Sequence used for male lots and animals.')
    semen_lot_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Extracted Semen Lots' Sequence",
        domain=[('code', '=', 'stock.lot')])
    dose_lot_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Semen Dose Lots' Sequence",
        domain=[('code', '=', 'stock.lot')])
    has_female = fields.Boolean(string='Females',
                                help="In this farm there are females.")
    female_sequence = fields.Many2one(
        comodel_name='ir.sequence', string="Females' Sequence",
        domain=[('code', '=', 'farm.animal')],
        help='Sequence used for female production lots and animals.')
    has_individual = fields.Boolean(string='Individuals',
                                    help="In this farm there are individuals.")
    individual_sequence = fields.Many2one(
        comodel_name='ir.sequence',
        string="Individuals' Sequence", domain=[('code', '=', 'farm.animal')],
        help="Sequence used for individual lots and animals.")
    has_group = fields.Boolean(string='Groups',
                               help="In this farm there are groups.")
    group_sequence = fields.Many2one(
        comodel_name='ir.sequence', string="Groups' Sequence",
        domain=[('code', '=', 'farm.animal.group')],
        help='Sequence used for group production lots and animals.')


class SpecieModel(models.Model):
    'Specie - Model'

    _name = 'farm.specie.ir.model'
    specie = fields.Many2one(comodel_name='farm.specie', string='Specie',
                             ondelete='CASCADE',
                             required=True, select=True)
    model = fields.Many2one(comodel_name='ir.model', string='Model',
                            required=True, select=True)
