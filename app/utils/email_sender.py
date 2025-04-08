import logging
import smtplib
from email.message import EmailMessage

from jinja2 import Template

from core import settings

TEMPLATE_DICT = {
    "verification": {
        "template": "verification_template.html",
        "subject": "Запрос на верификацию",
    },
    "verify_confirmation": {
        "template": "verify_confirmation_template.html",
        "subject": "Подтверждение верификации",
    },
}

TEMPLATES_DIR = "utils/email_templates/"


async def send_verification_email(
    user_email: str,
    token: str,
    action: str,
    url_verification: str = "",
) -> None:
    if not (action_dict := TEMPLATE_DICT.get(action)):
        return
    # Создаем объект сообщения
    mail_params = settings.email
    msg = EmailMessage()
    msg["From"] = mail_params.admin_email
    msg["To"] = mail_params.admin_email if action == "verification" else user_email
    msg["Subject"] = action_dict.get("subject", "")

    with open(TEMPLATES_DIR + action_dict.get("template", ""), "r") as file:
        template_content = file.read()

    template = Template(template_content)

    rendered_html_content = template.render(
        user_email=user_email,
        url_verification=url_verification,
        token=token,
    )

    msg.add_alternative(rendered_html_content, subtype="html")

    # Настройка SMTP сервера и отправка сообщения
    try:
        with smtplib.SMTP(mail_params.host, mail_params.port) as server:
            server.starttls()  # Запускаем шифрование TLS
            server.login(
                mail_params.admin_email, password=mail_params.password
            )  # Логинимся на сервере
            server.send_message(msg)  # Отправляем сообщение
    except Exception as e:
        logging.error(f"Ошибка при отправке письма: {e}")
