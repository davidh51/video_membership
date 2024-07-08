from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_FROM_NAME = settings.MAIL_FROM_NAME,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="app/mail/templates"
)    

async def send_registration_mail(subject : str, email_to : str, body : dict):
    message = MessageSchema(
        subject = subject,
        recipients = [email_to],
        template_body = body,
        subtype = "html"
    )

    fm = FastMail(conf)
    await fm.send_message(message=message, template_name="email.html")

async def password_reset(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject = subject,
        recipients = [email_to],
        template_body = body,
        subtype = "html"
    )

    fm = FastMail(conf)
    await fm.send_message(message=message, 
                          template_name="password_reset.html")

