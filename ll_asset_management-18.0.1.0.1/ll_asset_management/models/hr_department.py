
from odoo import fields, models, api, _


class LLAssetHRDepartment(models.Model):
    _inherit = 'hr.department'

    asset_location_id = fields.Many2one('ll.asset.location', string="Asset Location")
