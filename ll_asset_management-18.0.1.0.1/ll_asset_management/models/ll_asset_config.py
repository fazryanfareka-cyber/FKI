from odoo import fields, models, api, _


class LLAssetLocation(models.Model):
    _name = 'll.asset.location'
    _description = "LL Asset Location"
    _inherit = ['ll.mixin.multi_company']

    name = fields.Char(string="Location Name", required=True)
    owner_id = fields.Many2one(
        'res.partner',
        string="Owner",
        default=lambda self: self.env.company.partner_id,
        domain=[('is_company', '=', True)], index = True, required=True
    )
    location_for = fields.Selection([
        ('asset_stock', 'Asset Stock'),
        ('requester', 'Requester'),
        ('repair_center', 'Repair Center'),
        ('dispose', 'Disposed Asset'),
    ], default='asset_stock', string="Location For")
    note = fields.Html(string='Note', translate=True)

    total_asset = fields.Integer(string='Total Assets', compute='_get_count_list')

    def _get_count_list(self):
        for record in self:
            record.total_asset = self.env['ll.asset.asset'].search_count([
                ('asset_active_loc_id', '=', record.id)
            ])

    def action_btn_assets(self):
        tree_view = self.env.ref('ll_asset_management.view_ll_asset_asset_list')

        return {
            'name': _('Asset'),
            'type': 'ir.actions.act_window',
            'res_model': 'll.asset.asset',
            'view_mode': 'list,form',
            'views': [(tree_view.id, 'list'), (False, 'form')],
            'target': 'current',
            'domain': [('asset_active_loc_id', 'in', self.ids)],
        }

class LLAssetCategory(models.Model):
    _name = 'll.asset.category'
    _description = "LL Asset Category"

    name = fields.Char(string="Name", required=True)
    desc = fields.Text(string='Description')

