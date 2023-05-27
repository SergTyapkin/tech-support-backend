import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from src.utils.utils import read_app_config

import smtplib
from email.mime.text import MIMEText
from datetime import datetime

config = read_app_config('./configs/config.json')

DB_NAME = "tech-support"
MAIL_RECIPIENT = config["mail_address"]
MAIL_HTML = """<html>
  <head></head>
  <body>
    <h1>Ура, новый бэкап!</h1>
  </body>
</html>"""
BACKUPS_DIR = "/pg_backups"


if __name__ == '__main__':
    WEEKDAY = datetime.today().strftime('%A')
    FILE_NAME = f"backup_{WEEKDAY}.sql.backup"
    FILE_PATH = os.path.join(BACKUPS_DIR, FILE_NAME)

    msg = MIMEMultipart()
    msg['Subject'] = f"{WEEKDAY}(GMT) Backup of {DB_NAME}"
    msg['From'] = config["mail_sender_name"]
    msg['To'] = MAIL_RECIPIENT
    msg.attach(MIMEText(MAIL_HTML, 'html'))
    with open(FILE_PATH, "r") as f:
        part = MIMEApplication(
            f.read(),
            Name=FILE_NAME
        )
    # After the file is closed
    part['Content-Disposition'] = f'attachment; filename="{FILE_NAME}"'
    msg.attach(part)

    server = smtplib.SMTP(host=config["SMTP_mail_server_host"], port=config["SMTP_mail_server_port"])
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(config["mail_address"], config["mail_password"])
    server.send_message(msg)
    server.quit()
    print('Successfully sent the mail!')
