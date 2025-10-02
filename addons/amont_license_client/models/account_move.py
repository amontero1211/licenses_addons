from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    is_amont_license_valid = fields.Boolean(related="company_id.is_amont_license_valid")

    @api.model_create_multi
    def create(self, vals_list):
        # Ensure that the company has a valid Amont license before creating an account move
        for vals in vals_list:
            if not vals.get("company_id"):
                continue
            
            company = self.env["res.company"].browse(vals["company_id"])
            if not company.is_amont_license_valid:
                raise UserError(_("Cannot create account move: Amont license is not active for this company."))
        
        return super().create(vals_list)


    def validate_amont_license(self):
        print("Validating Amont license for account move...")
        return self.is_amont_license_valid

    @api.model
    def get_view(self, view_id=None, view_type='form', **kwargs):
        if view_type == "tree":
            self.env.company._compute_amont_license()
            model_id = self.env.company.env["ir.model"].search([("model", "=", "account.move")], limit=1)
            access_records = self.env.company.env['ir.model.access'].search([('model_id', '=', model_id.id)])
            for access in access_records:
                access.write({
                    'perm_write': self.env.company.is_amont_license_valid,
                    'perm_create': self.env.company.is_amont_license_valid,
                    'perm_unlink': self.env.company.is_amont_license_valid,
                })
        return super().get_view(view_id, view_type, **kwargs)