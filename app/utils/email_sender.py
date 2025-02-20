import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core import settings


async def send_verification_email(user_email: str, url_verification: str):
    # Создаем объект сообщения
    mail_params = settings.email
    msg = MIMEMultipart()
    msg["From"] = mail_params.from_email
    msg["To"] = mail_params.to_email
    msg["Subject"] = "Запрос на верификацию"

    # Добавляем текстовое сообщение
    msg.attach(
        MIMEText(
            f"Ссылка на верификацию пользователя {user_email}:\n{url_verification}",
            "plain",
        )
    )

    # Настройка SMTP сервера и отправка сообщения
    try:
        with smtplib.SMTP(mail_params.host, mail_params.port) as server:
            server.starttls()  # Запускаем шифрование TLS
            server.login(
                mail_params.from_email, password=mail_params.password
            )  # Логинимся на сервере
            server.send_message(msg)  # Отправляем сообщение
    except Exception as e:
        logging.error(f"Ошибка при отправке письма: {e}")
