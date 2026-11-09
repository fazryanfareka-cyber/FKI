from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from markupsafe import Markup

class LLAssetIssuance(models.Model):
    _name = 'll.asset.issuance'
    _description = "Asset Issuance"
    _order = "name desc"
    _inherit = ['ll.mixin.multi_company', 'll.mixin.asset_management', 'll.asset.action.mixin', 'mail.thread', 'mail.activity.mixin']

    company_partner_id = fields.Many2one(
        'res.partner',
        string="Company Partner",
        related='company_id.partner_id',
        help="This field is for the partner of active/current company"
    )

    name = fields.Char(string="Reference No.", readonly=True, copy=False)
    expected_date = fields.Date(string="Expected Date")
    received_date = fields.Date(string="Received Date", readonly=True)
    notes = fields.Html(string="Notes")
    state = fields.Selection([('draft', "Draft"),
                              ('submitted', "Waiting for Validation"),
                              ('validated', "Validated"),
                              ('approved', "Approved"),
                              ('issued', 'Issued'),
                              ('cancelled', "Cancelled"),
                              ('rejected', "Rejected")
                              ], default='draft', tracking=True)
    asset_issuance_line_ids = fields.One2many('ll.asset.issuance.line', 'asset_issuance_id', string="Asset lines")

    # *********************** on change *********************************

    # *********************** computed function **********************************

    # *********************** default/inherited function **********************************
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('location_id'):
                raise ValidationError("Please select a location before proceeding. The location is required.")

            if not vals.get('name'):
                company = self.env.company
                seq_code = f'll.asset.issuance.sequence.{company.id}'

                seq = self.env['ir.sequence'].with_company(company).next_by_code(seq_code)

                if not seq:
                    seq = self.env['ir.sequence'].next_by_code('ll.asset.issuance.sequence')

                if not seq:
                    raise ValidationError(_("No issuance sequence found for Company %s, and fallback failed.") % company.name)

                vals['name'] = seq

        rec = super().create(vals_list)
        rec.check_duplicate_assets_in_lines(rec.asset_issuance_line_ids)

        if rec.requester_employee_id:
            rec.requester_employee_id.sudo().asset_location_id = rec.location_id

        if rec.requester_company_id:
            rec.requester_company_id.sudo().asset_location_id = rec.location_id

        if rec.requester_department_id:
            rec.requester_department_id.sudo().asset_location_id = rec.location_id

        return rec

    def write(self, vals):
        if 'location_id' in vals and not vals['location_id']:
            raise ValidationError("Please select a location before proceeding. The location is required.")

        res = super().write(vals)
        self.check_duplicate_assets_in_lines(self.asset_issuance_line_ids)
        for rec in self:
            if rec.requester_employee_id:
                rec.requester_employee_id.sudo().asset_location_id = rec.location_id

            if rec.requester_company_id:
                rec.requester_company_id.sudo().asset_location_id = rec.location_id

            if rec.requester_department_id:
                rec.requester_department_id.sudo().asset_location_id = rec.location_id
        return res

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("Only records in draft state can be deleted.")
        return super().unlink()


    # ********************************** Function/methods **********************************

    # *********************** action/button function **********************************
    def _update_asset_asset(self):
        for rec in self:
            assets = rec.mapped('asset_issuance_line_ids.asset_id')
            rec._update_assets(assets, {
                'state': 'available',
                'asset_issuance_id': False,
                'issuance_status': False,
            })
            rec._post_asset_message(assets, 'll.asset.issuance', rec.id, rec.name, "Available", 'Asset Issuance')

    def action_btn_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec._update_asset_asset()

    def action_btn_submit(self):
        for rec in self:
            if not rec.asset_issuance_line_ids:
                raise ValidationError("No asset selected.")

            valid_states = ['available']
            if self.env.context.get('allow_replacement_state'):
                valid_states.append('rep_processing')

            invalid_assets = rec.asset_issuance_line_ids.filtered(
                lambda l: l.asset_id.state not in valid_states
            )

            if invalid_assets:
                asset_names = ', '.join(invalid_assets.mapped('asset_id.name'))
                raise ValidationError(
                    f"The following assets are not in 'Available' state anymore and cannot be issued: {asset_names}"
                )

            rec.state = 'submitted'
            assets = rec.mapped('asset_issuance_line_ids.asset_id')
            rec._update_assets(assets, {
                'state': 'req_processing',
                'asset_issuance_id': rec.id,
                'issuance_status': rec.get_selection_label('ll.asset.issuance', 'state', rec.state),
            })
            rec._post_asset_message(assets, 'll.asset.issuance', rec.id, rec.name, "Processing (Issuance)", 'Asset Issuance')

    def action_btn_validate(self):
        for rec in self:
            rec.state = 'validated'
            assets = rec.mapped('asset_issuance_line_ids.asset_id')
            rec._update_assets(assets, {
                'issuance_status': rec.get_selection_label('ll.asset.issuance', 'state', rec.state),
            })

    def action_btn_approve(self):
        for rec in self:
            rec.state = 'approved'
            assets = rec.mapped('asset_issuance_line_ids.asset_id')
            rec._update_assets(assets, {
                'issuance_status': rec.get_selection_label('ll.asset.issuance', 'state', rec.state),
            })

    def action_btn_issue(self):
        for rec in self:
            rec.state = 'issued'
            assets = rec.mapped('asset_issuance_line_ids.asset_id')
            rec._update_assets(assets, {
                'state': 'allocated',
                'asset_active_loc_id': rec.location_id.id,
                'issuance_status': rec.get_selection_label('ll.asset.issuance', 'state', rec.state),
            })
            rec._post_asset_message(assets, 'll.asset.issuance', rec.id, rec.name, "Allocated", 'Asset Issuance')

    def action_btn_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
            rec._update_asset_asset()

    def action_btn_reject(self):
        for rec in self:
            invalid_operation = rec.asset_issuance_line_ids.filtered(
                lambda l: l.asset_id.asset_issuance_id.id != rec.id)
            if invalid_operation:
                asset_names = ', '.join(invalid_operation.mapped('asset_id.name'))
                raise ValidationError(
                    f"The following assets have new transaction and cannot be rejected: {asset_names}"
                )

            rec.state = 'rejected'
            assets = rec.mapped('asset_issuance_line_ids.asset_id')
            for asset in assets:
                asset.asset_active_loc_id = asset.asset_loc_id.id

            rec._update_assets(assets, {
                'state': 'available',
                'asset_issuance_id': False,
                'issuance_status': False,
            })
            rec._post_asset_message(assets, 'll.asset.issuance', rec.id, rec.name, "Available", 'Asset Issuance')


class LLAssetIssuanceLine(models.Model):
    _name = 'll.asset.issuance.line'
    _description = "LL Asset Issuance Lines"

    asset_issuance_id = fields.Many2one('ll.asset.issuance', string="Asset Issuance ID", ondelete='cascade')

    source_location_id = fields.Many2one('ll.asset.location', string="Source Location", required=True)
    asset_id = fields.Many2one('ll.asset.asset', string="Asset", required=True)
    serial_number = fields.Char(string="Serial Number", related='asset_id.serial_number')
    asset_category_id = fields.Many2one('ll.asset.category', string="Category", related='asset_id.asset_category_id')
    remarks = fields.Text(string="Remarks")

    @api.onchange('source_location_id')
    def _onchange_source_location_id(self):
        self.asset_id = False
