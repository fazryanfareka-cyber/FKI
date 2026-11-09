
from odoo import fields, models, api, _


class LLAssetResPartner(models.Model):
    _inherit = 'res.partner'

    asset_location_id = fields.Many2one('ll.asset.location', string="Asset Location")
