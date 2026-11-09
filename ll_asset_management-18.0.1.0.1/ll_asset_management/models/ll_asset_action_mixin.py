from odoo import models, _
from markupsafe import Markup

class AssetActionMixin(models.AbstractModel):
    _name = 'll.asset.action.mixin'
    _description = 'Asset Action Helper Mixin'

    def _update_assets(self, assets, vals):
        if assets:
            assets.sudo().write(vals)

    def _post_asset_message(self, assets, model_name, record_id, record_name, new_status_label, transaction):
        link = "/web#model=%s&id=%s&view_type=form" % (model_name, record_id)
        html_link = "<a href='%s'>%s</a>" % (link, record_name)
        message = Markup("<p>Asset status changed to <b>%s</b> via %s: %s</p>" %
                         (new_status_label, transaction, html_link))
        for asset in assets:
            asset.sudo().message_post(body=message)
