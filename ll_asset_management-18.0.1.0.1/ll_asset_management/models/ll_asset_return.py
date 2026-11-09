from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from markupsafe import Markup

class LLAssetReturn(models.Model):
    _name = 'll.asset.return'
    _description = "Asset Return"
    _order = "name desc"
    _inherit = ['ll.mixin.multi_company', 'll.mixin.asset_management', 'll.asset.action.mixin', 'mail.thread', 'mail.activity.mixin']

    company_partner_id = fields.Many2one(
        'res.partner',
        string="Company Partner",
        related='company_id.partner_id',
        help="This field is for the partner of active/current company"
    )

    name = fields.Char(string="Reference No.", readonly=True, copy=False)
    return_date = fields.Date(string="Return Date", readonly=True)
    notes = fields.Html(string="Notes")
    state = fields.Selection([('draft', "Draft"),
                              ('submitted', "Waiting for Validation"),
                              ('validated', "Validated"),
                              ('approved', "Approved"),
                              ('returned', 'Returned'),
                              ('cancelled', "Cancelled"),
                              ('rejected', "Rejected")
                              ], default='draft', tracking=True)

    asset_return_line_ids = fields.One2many('ll.asset.return.line', 'asset_return_id', string="Asset Return lines")

    # ********************************** Function/methods **********************************
    def _search_assets(self, loc, requester_type, requester, status):
        self.ensure_one()

        lines = [(5, 0, 0)]

        assets = self.env['ll.asset.asset'].search([
            (requester_type, '=', requester),
            ('state', '=', status),
            ('asset_active_loc_id', '=', loc)
        ])

        for asset in assets:
            lines.append((0, 0, {
                'asset_id': asset.id,
                'destination_location_id': asset.asset_loc_id.id,
            }))

        self.asset_return_line_ids = lines

    # ********************************** onchange **********************************
    @api.onchange('requester_employee_id', 'requester_company_id_id', 'requester_department_id', 'location_id')
    def _onchange_location_id(self):
        self.asset_return_line_ids = False

        if self.requester_employee_id:
            self._search_assets(self.location_id.id, 'issuance_req_emp_id', self.requester_employee_id.id, 'allocated')

        if self.requester_company_id:
            self._search_assets(self.location_id.id, 'issuance_req_company_id', self.requester_company_id.id, 'allocated')

        if self.requester_department_id:
            self._search_assets(self.location_id.id, 'issuance_req_dept_id', self.requester_department_id.id, 'allocated')

        # *********************** default/inherited function **********************************
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('location_id'):
                raise ValidationError("Please select a location before proceeding. The location is required.")

            if not vals.get('name'):
                company = self.env.company
                seq_code = f'll.asset.return.sequence.{company.id}'

                seq = self.env['ir.sequence'].with_company(company).next_by_code(seq_code)

                if not seq:
                    seq = self.env['ir.sequence'].next_by_code('ll.asset.return.sequence')

                if not seq:
                    raise ValidationError(
                        _("No issuance sequence found for Company %s, and fallback failed.") % company.name)

                vals['name'] = seq

        rec = super().create(vals_list)
        rec.check_duplicate_assets_in_lines(rec.asset_return_line_ids)
        return rec

    def write(self, vals):
        if 'location_id' in vals and not vals['location_id']:
            raise ValidationError("Please select a location before proceeding. The location is required.")

        res = super().write(vals)
        self.check_duplicate_assets_in_lines(self.asset_return_line_ids)
        return res

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("Only records in draft state can be deleted.")
        return super().unlink()

    # *********************** action/button function **********************************
    def _update_asset_asset(self):
        for rec in self:
            assets = rec.mapped('asset_return_line_ids.asset_id')
            rec._update_assets(assets, {
                'state': 'allocated',
                'asset_return_id': False,
                'prev_asset_return_id': False,
                'return_status': False,
            })
            rec._post_asset_message(assets, 'll.asset.return', rec.id, rec.name, "Allocated", 'Asset Return')

    def action_btn_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec._update_asset_asset()

    def action_btn_submit(self):
        for rec in self:
            if not rec.asset_return_line_ids:
                raise ValidationError("No asset selected.")

            valid_states = ['allocated']
            if self.env.context.get('allow_replacement_state'):
                valid_states.append('rep_processing')

            invalid_assets = rec.asset_return_line_ids.filtered(
                lambda l: l.asset_id.state not in valid_states
            )
            if invalid_assets:
                asset_names = ', '.join(invalid_assets.mapped('asset_id.name'))
                raise ValidationError(
                    f"The following assets are not in a valid state and cannot be returned: {asset_names}"
                )

            rec.state = 'submitted'
            assets = rec.mapped('asset_return_line_ids.asset_id')

            rec._update_assets(assets, {
                'state': 'ret_processing',
                'asset_return_id': rec.id,
                'return_status': rec.get_selection_label('ll.asset.return', 'state', rec.state),
            })
            for asset in assets:
                asset.prev_asset_return_id = asset.asset_return_id.id

            rec._post_asset_message(assets, 'll.asset.return', rec.id, rec.name, "Processing (Return)", 'Asset Return')

    def action_btn_validate(self):
        for rec in self:
            rec.state = 'validated'
            assets_to_update = rec.mapped('asset_return_line_ids.asset_id')
            assets_to_update.sudo().write({
                'return_status': rec.get_selection_label('ll.asset.return', 'state', rec.state),
            })

    def action_btn_approve(self):
        for rec in self:
            rec.state = 'approved'
            assets_to_update = rec.mapped('asset_return_line_ids.asset_id')
            assets_to_update.sudo().write({
                'return_status': rec.get_selection_label('ll.asset.return', 'state', rec.state),
            })

    def action_btn_return(self):
        for rec in self:
            rec.state = 'returned'
            assets = rec.mapped('asset_return_line_ids.asset_id')

            for asset in assets:
                asset.asset_active_loc_id = asset.asset_loc_id.id
                asset.prev_asset_issuance_id = asset.asset_issuance_id.id
                asset.prev_asset_return_id = asset.asset_return_id.id

            rec._update_assets(assets, {
                'state': 'available',
                'asset_issuance_id': False,
                'asset_return_id': False,
                'issuance_status': False,
                'return_status': False,
            })
            rec._post_asset_message(assets, 'll.asset.return', rec.id, rec.name, "Available", 'Asset Return')

    def action_btn_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
            rec._update_asset_asset()

    def action_btn_reject(self):
        for rec in self:
            invalid_operation = rec.asset_return_line_ids.filtered(
                lambda l: l.asset_id.prev_asset_return_id.id != rec.id)
            if invalid_operation:
                asset_names = ', '.join(invalid_operation.mapped('asset_id.name'))
                raise ValidationError(
                    f"The following assets have new transaction and cannot be rejected: {asset_names}"
                )

            rec.state = 'rejected'

            assets_to_update = rec.mapped('asset_return_line_ids.asset_id')
            assets_to_update.sudo().write({
                'state': 'allocated',
                'asset_return_id': False,
                'prev_asset_return_id': False,
                'return_status': False,
            })

            rec._post_asset_message(assets_to_update, 'll.asset.return', rec.id, rec.name, "Allocated", 'Asset Return')

            for asset in assets_to_update:
                asset.asset_issuance_id = asset.prev_asset_issuance_id.id
                asset.asset_active_loc_id = asset.issuance_location_id.id
                asset.issuance_status = rec.get_selection_label('ll.asset.issuance', 'state', asset.asset_issuance_id.state)

class LLAssetReturnLine(models.Model):
    _name = 'll.asset.return.line'
    _description = "LL Asset Return Lines"

    asset_return_id = fields.Many2one('ll.asset.return', string="Asset Return ID", ondelete='cascade')

    asset_id = fields.Many2one('ll.asset.asset', string="Asset", required=True)
    serial_number = fields.Char(string="Serial Number", related='asset_id.serial_number')
    asset_category_id = fields.Many2one('ll.asset.category', string="Category", related='asset_id.asset_category_id')
    destination_location_id = fields.Many2one('ll.asset.location', string="Destination Location", related='asset_id.asset_loc_id')
    remarks = fields.Text(string="Remarks")

