from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
from datetime import timedelta


class ResCompany(models.Model):
    _inherit = "res.company"

    amont_license = fields.Char(
        "License Key",
        help="Enter the license key provided by Amont."
    )
    is_amont_license_valid = fields.Boolean(
        "Is License Valid",
        compute="_compute_amont_license",
        store=True,
        default=False,
    )

    api_url = fields.Char(
        "API URL",
        default="http://localhost:8069",
    )

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")

    @api.model
    def try_send_notification(self):
        companies = self.env["res.company"].search([])
        for company in companies:
            partner_ids = company.env['res.users'].search([])
            if not company.amont_license or not company.end_date:
                continue
            if company.end_date < fields.Date.today():
                company.env['bus.bus']._sendmany([[
                    partner_id.partner_id,
                    'amont_license_client',
                    {
                        'type': 'danger',
                        'title': 'Amont License',
                        'message': 'Your Amont License is expired. Please contact your administrator.',
                    }
                ] for partner_id in partner_ids])
            elif company.end_date - fields.Date.today() < timedelta(days=30):
                days_remaining = (company.end_date - fields.Date.today()).days
                company.env['bus.bus']._sendmany([[
                    partner_id.partner_id,
                    'amont_license_client',
                    {
                        'type': 'danger',
                        'title': 'Amont License',
                        'message': f'Your Amont License is about to expire in {days_remaining} days. Please contact your administrator.',
                    }
                ] for partner_id in partner_ids])

    def update_account_move_access(self):
        model_id = self.env["ir.model"].search(
            [("model", "=", "account.move")], limit=1)
        access_records = self.env['ir.model.access'].search(
            [('model_id', '=', model_id.id)])
        for access in access_records:
            access.write({
                # 'perm_read': self.is_amont_license_valid,
                'perm_write': self.is_amont_license_valid,
                'perm_create': self.is_amont_license_valid,
                'perm_unlink': self.is_amont_license_valid,
            })

    @api.model
    def validate_licenses(self, records):
        print("-------------------------------------")
        print("ResCompany -> validate_licenses")
        print("-------------------------------------")
        for company in records:
            # if not company.amont_license or (company.end_date and company.end_date < fields.Date.today()):
            if not company.amont_license:
                company.is_amont_license_valid = False

            # Yo tenia unos zapatos, blancos... Bien bonitos, y Andrea me los secuestro... :(
            else:
                try:
                    response = company._validate_license(company.amont_license)
                    company.is_amont_license_valid = "active" == response.get(
                        "state")
                    company.start_date = response.get("start_date")
                    company.end_date = response.get("end_date")
                except Exception as e:
                    company.is_amont_license_valid = False
                    raise UserError(
                        _("License validation failed: %s") % str(e))
            if company.end_date and company.end_date < fields.Date.today():
                company.is_amont_license_valid = False

    # @api.depends_context("amont_license", "api_url")

    @api.depends("amont_license", "api_url")
    def _compute_amont_license(self):
        print("-------------------------------------")
        print("ResCompany -> _compute_amont_license")
        print("-------------------------------------")
        self.validate_licenses(self)

    @api.model
    def auto_validate_license(self):
        companies = self.env["res.company"].search([])
        self.validate_licenses(companies)

    def _validate_license(self, license_key):
        print("-------------------------------------")
        print("ResCompany -> _validate_license")
        print("-------------------------------------")
        self.ensure_one()
        if not self.api_url:
            raise UserError(_("API URL is not configured"))
        res = requests.post(
            url=self.api_url + "/license/validate",
            json={
                "name": self.name,
                "database": self.env.cr.dbname,
                "license": license_key
            }
        ).json()

        return res.get("result", {})
