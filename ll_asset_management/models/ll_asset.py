from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class LLAssetAsset(models.Model):
    _name = 'll.asset.asset'
    _description = "Asset"
    _inherit = ['ll.mixin.multi_company', 'll.mixin.asset_management', 'mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)

    name = fields.Char(string="Name", required=True, tracking=True, copy=True)
    asset_category_id = fields.Many2one('ll.asset.category', string="Category")
    serial_number = fields.Char(string="Serial Number", tracking=True, copy=False)
    warranty_start = fields.Date(string="Warranty Start")
    warranty_end = fields.Date(string="Warranty End")

    asset_owner_id = fields.Many2one(
        'res.partner',
        string="Owner",
        domain=lambda self: self._domain_asset_owner(),
        default=lambda self: self.env.company.partner_id,
        required=True,
        tracking=True,
        check_company=True,
    )
    asset_loc_id = fields.Many2one('ll.asset.location', string="Owner Location", tracking=True,
                                   copy=True, domain="[('owner_id', '=', asset_owner_id), ('location_for', '=', 'asset_stock')]",
                                   required=True, check_company=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('req_processing', 'Processing (Issuance)'),
        ('ret_processing', 'Processing (Return)'),
        ('allocated', 'Allocated'),
    ], default='draft', string='Asset Status', copy=False, tracking=True, readonly=True)
    asset_active_loc_id = fields.Many2one('ll.asset.location', string="Active Location", readonly=True, check_company=True)

    description = fields.Html(string='Description', translate=True)
    asset_reference = fields.Char(string="Asset Reference", readonly=True)

    asset_issuance_id = fields.Many2one('ll.asset.issuance', string="Issuance Reference", readonly=True)
    issuance_req_type = fields.Selection(string="Issuance Type", related='asset_issuance_id.requester_type')
    issuance_req_emp_id = fields.Many2one('hr.employee', string="Issuance Employee", related='asset_issuance_id.requester_employee_id')
    issuance_req_dept_id = fields.Many2one('hr.department', string="Issuance Department",  related='asset_issuance_id.requester_department_id')
    issuance_req_dept_manager_id = fields.Many2one('hr.employee', string="Issuance Manager", related='issuance_req_dept_id.manager_id')
    issuance_req_company_id = fields.Many2one('res.partner', string="Issuance Company", related='asset_issuance_id.requester_company_id')
    issuance_req_company_emp_id = fields.Many2one('res.partner', string="Issuance Representative", related='asset_issuance_id.requester_company_employee_id')
    issuance_location_id = fields.Many2one('ll.asset.location', string="Issuance Location", related='asset_issuance_id.location_id')
    issuance_status = fields.Char(string="Issuance Status")
    prev_asset_issuance_id = fields.Many2one('ll.asset.issuance', string="Previous Issuance Reference", readonly=True)

    asset_return_id = fields.Many2one('ll.asset.return', string="Return Reference", readonly=True)
    return_req_type = fields.Selection(string="Return Type", related='asset_issuance_id.requester_type')
    return_req_emp_id = fields.Many2one('hr.employee', string="Return Employee", related='asset_return_id.requester_employee_id')
    return_req_dept_id = fields.Many2one('hr.department', string="Return Department", related='asset_return_id.requester_department_id')
    return_req_dept_manager_id = fields.Many2one('hr.employee', string="Return Manager", related='return_req_dept_id.manager_id')
    return_req_company_id = fields.Many2one('res.partner', string="Return Company", related='asset_return_id.requester_company_id')
    return_req_company_emp_id = fields.Many2one('res.partner', string="Return Representative", related='asset_return_id.requester_company_employee_id')
    return_location_id = fields.Many2one('ll.asset.location', string="Employee Location", related='asset_return_id.location_id')
    return_status = fields.Char(string="Return Status")
    prev_asset_return_id = fields.Many2one('ll.asset.return', string="Previous Return Reference", readonly=True)

    _sql_constraints = [
        ('serial_company_uniq',
         'unique(serial_number, company_id)',
         'Serial number must be unique per company!')
    ]

    # *********************** on change **********************************
    @api.onchange('asset_owner_id')
    def _onchange_asset_owner_id(self):
        self.asset_loc_id = False

    # *********************** default/inherited function **********************************
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('asset_reference'):
                company = self.env.company
                seq_code = f'll.asset.asset.sequence.{company.id}'

                seq = self.env['ir.sequence'].with_company(company).next_by_code(seq_code)

                if not seq:
                    seq = self.env['ir.sequence'].next_by_code('ll.asset.asset.sequence')

                if not seq:
                    raise ValueError(_("No asset sequence found for Company %s, and fallback failed.") % company.name)

                vals['asset_reference'] = seq

            if vals.get('asset_loc_id'):
                vals['asset_active_loc_id'] = vals['asset_loc_id']
        return super().create(vals_list)

    def write(self, vals):
        if 'asset_loc_id' in vals:
            vals['asset_active_loc_id'] = vals['asset_loc_id']

        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("Only records in draft state can be deleted.")
        return super().unlink()

    # *********************** for domain/filter **********************************
    @api.model
    def _domain_asset_owner(self):
        allowed_companies = self.env.context.get('allowed_company_ids')
        if allowed_companies and len(allowed_companies) > 1:
            return [('is_company', '=', True),
                    '|',
                    ('company_id', 'in', allowed_companies),
                    ('company_id', '=', False)]
        else:
            return [('is_company', '=', True)]

    # *********************** action header button **********************************
    def action_asset_draft(self):
        for rec in self:
            if rec.state != 'available':
                raise ValidationError(
                "Cannot set to draft. The asset's status may have changed. Please reload the page to view the latest status."
            )

            rec.write({
                'state': 'draft',
            })
        
    def action_asset_confirm(self):
        self.ensure_one()
        self.write({
            'state': 'available',
        })