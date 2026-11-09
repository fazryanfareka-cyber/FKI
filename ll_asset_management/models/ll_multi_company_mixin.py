from odoo import models, fields, api

class MultiCompanyMixin(models.AbstractModel):
    _name = 'll.mixin.multi_company'
    _description = 'Multi-Company Mixin'

    company_id = fields.Many2one(
        'res.company',
        string="Company ID",
        default=lambda self: self.env.company,
        required=True,
        index=True,
        domain=lambda self: [('id', 'in', self.env.companies.ids)]
    )

    show_company = fields.Boolean(
        compute='_compute_show_company',
        store=False
    )

    current_company_id = fields.Many2one(
        'res.company',
        compute='_compute_current_company_id',
        store=False
    )

    @api.depends('company_id')
    @api.depends_context('allowed_company_ids')
    def _compute_show_company(self):
        for rec in self:
            rec.show_company = len(self.env.companies) > 1

    @api.depends('company_id')
    def _compute_current_company_id(self):
        for rec in self:
            rec.current_company_id = self.env.company
