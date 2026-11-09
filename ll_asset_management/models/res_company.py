from datetime import date

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    code = fields.Char(string="Short Code", help="Short company identifier used in asset references.")

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        for company in companies:
            # code = (company.code or company.name or "GEN").upper().replace(" ", "")
            if company.code:
                code = company.code.upper()
            else:
                code = ''.join(word[0] for word in company.name.split()).upper()

            year = str(date.today().year)

            self.env['ir.sequence'].create({
                'name': f"Asset Sequence - {company.name}",
                'code': f'll.asset.asset.sequence.{company.id}',
                'prefix': f"ASSET/{code}/{year}/",
                'padding': 5,
                'number_increment': 1,
                'company_id': company.id,
            })

            self.env['ir.sequence'].create({
                'name': f"Asset Issuance Sequence - {company.name}",
                'code': f'll.asset.issuance.sequence.{company.id}',
                'prefix': f"ASSET-ISS/{code}/{year}/",
                'padding': 5,
                'number_increment': 1,
                'company_id': company.id,
            })

            self.env['ir.sequence'].create({
                'name': f"Asset Return Sequence - {company.name}",
                'code': f'll.asset.return.sequence.{company.id}',
                'prefix': f"ASSET-RET/{code}/{year}/",
                'padding': 5,
                'number_increment': 1,
                'company_id': company.id,
            })

            # if company.partner_id:
            #     company.partner_id.company_id = company.id

        return companies