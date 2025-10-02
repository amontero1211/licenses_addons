from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import uuid
import hashlib
import logging

_logger = logging.getLogger(__name__)


STATE = [
    ("active", "Active"),
    ("expired", "Expired")
]


class ServerClient(models.Model):
    _name = "amont.server.client"
    _inherit = ['portal.mixin', 'mail.thread.main.attachment',
                'mail.activity.mixin']
    _description = "Customers associated with the server"

    name = fields.Char(string="Company Name", required=True)
    database = fields.Char(string="Database Name", required=True)
    license = fields.Char(string="License Key", readonly=True)
    state = fields.Selection(STATE, compute="_compute_state")
    start_date = fields.Date()
    end_date = fields.Date()
    partner_id = fields.Many2one("res.partner", string="Partner")
    email = fields.Char(related="partner_id.email")

    reminder_30_days_sent = fields.Boolean(
        "30 Days Reminder Sent", default=False)
    reminder_15_days_sent = fields.Boolean(
        "15 Days Reminder Sent", default=False)
    reminder_7_days_sent = fields.Boolean(
        "7 Days Reminder Sent", default=False)
    reminder_3_days_sent = fields.Boolean(
        "3 Days Reminder Sent", default=False)
    reminder_1_day_sent = fields.Boolean("1 Day Reminder Sent", default=False)
    reminder_expired_sent = fields.Boolean(
        "Expired Reminder Sent", default=False)

    @api.depends("start_date", "end_date")
    def _compute_state(self):
        for client in self:
            if client.start_date and client.end_date:
                flag = client.start_date <= fields.Date.today() <= client.end_date
                client.state = "active" if flag else "expired"
            else:
                client.state = "expired"

    def generate_license(self):
        # Generar un UUID aleatorio
        generated_uuid = uuid.uuid4()

        # Crear un hash SHA-256 para mayor seguridad
        hash_license = hashlib.sha256(str(generated_uuid).encode()).hexdigest()

        # Formatear la clave de licencia
        self.license = "-".join([hash_license[i:i+5]
                                for i in range(0, 25, 5)]).upper()
        self.start_date = fields.Date.today()
        self.end_date = fields.Datetime.now() + relativedelta(years=1)

    @api.model
    def validate_license(self, client, database, license):
        return self.search_read([
            ("name", "=", client),
            ("database", "=", database),
            ("license", "=", license),
        ], fields=["name", "database", "license", "state", "start_date", "end_date"])

    @api.model
    def try_send_notification(self):
        clients = self.env["amont.server.client"].search([])
        for client in clients:
            if not client.license or not client.end_date:
                continue

            days_remaining = (client.end_date - fields.Date.today()).days

            # Get all users with a specific permission (e.g., 'base.group_system') to send emails to
            partner = client.partner_id

            # Check if license has expired
            if client.end_date <= fields.Date.today():
                if not client.reminder_expired_sent:
                    _logger.info(
                        f"License expired for company {client.name}. Sending expired notification.")
                    client._send_license_expired_email(partner)
                    client.reminder_expired_sent = True

            # Check for specific day reminders
            elif days_remaining <= 30 and not client.reminder_30_days_sent:
                _logger.info(
                    f"License expires in 30 days for company {client.name}. Sending reminder.")
                client._send_license_reminder_email(partner, 30)
                client.reminder_30_days_sent = True
            elif days_remaining <= 15 and not client.reminder_15_days_sent:
                _logger.info(
                    f"License expires in 15 days for company {client.name}. Sending reminder.")
                client._send_license_reminder_email(partner, 15)
                client.reminder_15_days_sent = True
            elif days_remaining <= 7 and not client.reminder_7_days_sent:
                _logger.info(
                    f"License expires in 7 days for company {client.name}. Sending reminder.")
                client._send_license_reminder_email(partner, 7)
                client.reminder_7_days_sent = True
            elif days_remaining <= 3 and not client.reminder_3_days_sent:
                _logger.info(
                    f"License expires in 3 days for company {client.name}. Sending reminder.")
                client._send_license_reminder_email(partner, 3)
                client.reminder_3_days_sent = True
            elif days_remaining <= 1 and not client.reminder_1_day_sent:
                _logger.info(
                    f"License expires in 1 day for company {client.name}. Sending reminder.")
                client._send_license_reminder_email(partner, 1)
                client.reminder_1_day_sent = True

    def _send_license_reminder_email(self, partner, days_remaining):
        """Send license expiration reminder email to users"""
        self.ensure_one()

        template = self.env.ref(
            'amont_license_server.mail_template_license_expiration_reminder')

        if partner.email:
            ctx = {
                'partner_id': partner.id,
                'partner_name': partner.name,
                'days_remaining': days_remaining,
                'lang': partner.lang,
                'company_name': self.name,
                'end_date': self.end_date,
            }
            template.with_context(ctx).send_mail(self.id, force_send=True)

    def _send_license_expired_email(self, partner_id):
        """Send license expired email to users"""
        self.ensure_one()

        template = self.env.ref(
            'amont_license_server.mail_template_license_expired')

        if partner_id.email:
            ctx = {
                'partner_id': partner_id.id,
                'partner_name': partner_id.name,
                'lang': partner_id.lang,
            }
            template.with_context(ctx).send_mail(self.id, force_send=True)

    def reset_reminder_flags(self):
        """Reset all reminder flags when license is renewed"""
        self.ensure_one()
        self.write({
            'reminder_30_days_sent': False,
            'reminder_15_days_sent': False,
            'reminder_7_days_sent': False,
            'reminder_3_days_sent': False,
            'reminder_1_day_sent': False,
            'reminder_expired_sent': False,
        })
