import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from common.secrets import (
    EMAIL_BACKEND,
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_USE_TLS,
    EMAIL_HOST_USER,
    MAIL_PASS
)


class SenderMail:

    def __init__(self, from_email, to_emails, signature="", enterprise=""):
        self.SMTP_USER = from_email['user']
        self.SMTP_PASSWORD = from_email['password']
        self.SMTP_PORT = 587
        self.con_satus = False
        self.SMTP_SERVER = "smtp.office365.com"
        self.server = None
        self.signature = signature
        self.enterprise = enterprise
        self.erro_mail_address = []

        if self.validate_email(to_email):
            self.login()
            self.send_email(to_email)
            self.close_connection()
            return True
        else:
            return False

    def login(self):
        try:
            self.server = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
            self.server.starttls()
            self.server.login(self.SMTP_USER, self.SMTP_PASSWORD)
            self.con_satus = True
        except Exception as e:
            self.con_satus = False
            return False

    def validate_email(self, email):
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, email) is not None

    def get_message(self):
        html_content = """
       <html lang="es">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmación Kosmo Flowers</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #4a5568; background-color: #f7fafc; padding: 30px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; border: 1px solid #e96c23; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;">
                <img src="https://kosmoflowers.com/wp-content/uploads/2022/07/Mesa-de-trabajo-6.svg" alt="Kosmo Flowers" style="max-width: 200px; margin-bottom: 20px;">
                <p style="font-size: 16px; margin-bottom: 16px;">
                    Estimado(a) Cliente,<br><br>
                    Su solicitud fue recibida con éxito y se validará próximamente.  
                    Agradecemos su interés en trabajar Kosmo Flowers. Muy pronto estaremos en contacto.
                </p>
                <p style="font-size: 16px; margin-top: 24px; color: #2d3748;">
                    Atentamente,<br><br>
                    <strong style="font-size: 18px; color: #2d3748;">Kosmo Flowers</strong><br>
                    <em style="color: #718096;">www.kosmoflowers.com</em>
                </p>
            </div>
            </body>
            </html>
        """
        return {
            "html_content": html_content,
            "subject": "Confirmación de registro Kosmo Flowers"
        }

    def send_email(self, to_email):
        message = self.get_message()
        msg = MIMEMultipart("alternative")
        msg["From"] = self.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = message["subject"]
        msg["Disposition-Notification-To"] = self.SMTP_USER
        msg["Return-Receipt-To"] = 'notificaciones@dev-7.com'
        msg.attach(MIMEText(message['html_content'], "html"))

        try:
            self.server.sendmail(self.SMTP_USER, to_email, msg.as_string())
            return True
        except Exception as e:
            raise Exception("Error al enviar correo {to_email} {error}".format(
                to_email=to_email, error=e
            ))

    def close_connection(self):
        if self.con_satus and self.server:
            self.con_satus = False
            self.server.quit()
            print("Conexión cerrada")
