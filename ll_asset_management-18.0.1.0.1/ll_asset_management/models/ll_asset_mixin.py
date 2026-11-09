from odoo import models, fields, api, _

from odoo.exceptions import ValidationError
from markupsafe import Markup


class LLMixinAssetManagement(models.AbstractModel):
    _name = 'll.mixin.asset_management'
    _description = 'Asset Management Details'

    requester_type = fields.Selection([
        ('is_employee', "Employee"),
        ('is_company', "Company"),
        ('is_department', "Department"),
    ], string="Requester Type", default='is_employee')

    helper_partner_id = fields.Many2one('res.partner', compute='_compute_helper_partner_id', store=False,
                                        help="This field is a helper for filtering location")
    requester_company_employee_ids = fields.Many2many('res.partner', compute='_compute_requester_company_employee_ids',
                                                      store=False)

    requester_employee_id = fields.Many2one('hr.employee', string="Employee", check_company=True)
    requester_department_id = fields.Many2one('hr.department', string="Department", check_company=True)
    requester_department_manager_id = fields.Many2one('hr.employee', string="Manager",
                                                      related='requester_department_id.manager_id')
    requester_company_id = fields.Many2one('res.partner', "Company", domain="[('is_company', '=', True)]")
    requester_company_employee_id = fields.Many2one('res.partner', "Representative",
                                                    domain="[('id', 'in', requester_company_employee_ids)]")
    location_id = fields.Many2one('ll.asset.location', string="Location", domain="[('owner_id', '=', helper_partner_id), ('location_for', '=', 'requester')]")
    status = fields.Char(string="Status")

    # *********************** computed function **********************************
    @api.depends('requester_employee_id', 'requester_company_id', 'requester_department_id')
    def _compute_helper_partner_id(self):
        for rec in self:
            rec.helper_partner_id = False
            if rec.requester_employee_id and rec.requester_employee_id.address_id:
                rec.helper_partner_id = rec.requester_employee_id.address_id

            if rec.requester_company_id:
                rec.helper_partner_id = rec.requester_company_id

            if rec.requester_department_id:
                rec.helper_partner_id = rec.requester_department_id.company_id.partner_id

    @api.depends('requester_company_id')
    def _compute_requester_company_employee_ids(self):
        for rec in self:
            if rec.requester_company_id:
                rec.requester_company_employee_ids = self.env['res.partner'].search([
                    ('parent_id', '=', rec.requester_company_id.id)
                ])
            else:
                rec.requester_company_employee_ids = self.env['res.partner'].browse()

    # *********************** onchange **********************************
    @api.onchange('requester_type')
    def _onchange_requester_type(self):
        self.requester_employee_id = False
        self.requester_company_id = False
        self.requester_company_employee_id = False
        self.requester_department_id = False
        self.requester_department_manager_id = False
        self.location_id = False

    @api.onchange('requester_employee_id')
    def _onchange_requester_employee_id(self):
        self.location_id = False
        if self.requester_employee_id and self.requester_employee_id.asset_location_id:
            self.location_id = self.requester_employee_id.asset_location_id.id

    @api.onchange('requester_company_id')
    def _onchange_requester_company_id(self):
        self.requester_company_employee_id = False
        self.location_id = False
        if self.requester_company_id and self.requester_company_id.asset_location_id:
            self.location_id = self.requester_company_id.asset_location_id.id

    @api.onchange('requester_department_id')
    def _onchange_requester_department_id(self):
        self.requester_department_manager_id = False
        self.location_id = False
        if self.requester_department_id and self.requester_department_id.asset_location_id:
            self.location_id = self.requester_department_id.asset_location_id.id

    # *********************** methods **********************************
    def check_duplicate_assets_in_lines(self, line_ids):
        for rec in self:
            asset_ids = [line.asset_id.id for line in line_ids if line.asset_id]
            if len(asset_ids) != len(set(asset_ids)):
                raise ValidationError("You cannot select the same asset more than once.")

    def get_selection_label(self, model_name, field_name, field_value):
        field = self.env[model_name].fields_get(allfields=[field_name]).get(field_name)
        if not field or 'selection' not in field:
            return field_value
        selection_dict = dict(field['selection'])
        return _(selection_dict.get(field_value, field_value))
