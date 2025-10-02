# Amont License Client

## Email Notification System

This module now includes an automated email notification system for license expiration reminders.

### Features

- **Automated Email Reminders**: Sends email notifications to all active users when licenses are about to expire
- **Multiple Reminder Points**: Sends reminders at 30, 15, 7, 3, and 1 days before expiration
- **Expired License Notification**: Sends urgent notification when license has expired
- **Duplicate Prevention**: Tracks which reminders have been sent to avoid duplicate emails
- **Auto-Reset**: Resets reminder flags when license is renewed

### Reminder Schedule

- **30 days before expiration**: First reminder
- **15 days before expiration**: Second reminder  
- **7 days before expiration**: Third reminder
- **3 days before expiration**: Fourth reminder
- **1 day before expiration**: Final reminder
- **On expiration day**: Urgent expired notification

### Configuration

1. **Email Templates**: Two email templates are provided:
   - `mail_template_license_expiration_reminder`: For upcoming expiration reminders
   - `mail_template_license_expired`: For expired license notifications

2. **Cron Job**: A scheduled task runs every minute to check for licenses that need reminders

3. **Tracking Fields**: The following boolean fields track which reminders have been sent:
   - `reminder_30_days_sent`
   - `reminder_15_days_sent`
   - `reminder_7_days_sent`
   - `reminder_3_days_sent`
   - `reminder_1_day_sent`
   - `reminder_expired_sent`

### How It Works

1. The cron job `ir_cron_amont_license_client_date_checker` runs every minute
2. It checks all companies with valid licenses and end dates
3. For each company, it calculates days remaining until expiration
4. If the days remaining match one of the reminder points (30, 15, 7, 3, 1) and no reminder has been sent yet, it sends an email to all active users
5. If the license has expired and no expired notification has been sent, it sends an urgent notification
6. When a license is renewed (validated and has a future end date), all reminder flags are reset

### Email Recipients

Emails are sent to all active users in the system who have email addresses configured.

### Customization

You can customize the email templates by:
1. Going to Settings > Technical > Email > Templates
2. Finding the "Amont License" templates
3. Modifying the subject, body, or styling as needed

### Troubleshooting

- Check the Odoo logs for messages starting with "License expires in..." or "License expired for..."
- Verify that users have email addresses configured
- Ensure the cron job is active and running
- Check that the email templates are properly installed 