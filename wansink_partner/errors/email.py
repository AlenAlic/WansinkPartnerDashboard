from flask import render_template, current_app
from wansink_partner.email import send_email


def send_error_email(code, msg):
    send_email('WP Dashboard error: {}'.format(code),
               recipients=[current_app.config['ADMIN']],
               text_body=render_template('email/error.txt', message=msg),
               html_body=render_template('email/error.html', message=msg))
    send_email('Automatiserings Error',
               recipients=[current_app.config['RECIPIENTS']],
               text_body=render_template('email/admin_notified.txt'),
               html_body=render_template('email/admin_notified.html'))
