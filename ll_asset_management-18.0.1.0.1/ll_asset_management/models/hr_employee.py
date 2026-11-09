
from odoo import fields, models, api, _


class LLAssetHREmployee(models.AbstractModel):
    _inherit = "hr.employee.base"

    asset_location_id = fields.Many2one('ll.asset.location', string="Asset Location")