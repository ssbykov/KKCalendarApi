import random

import translators as ts
from translators.server import TranslatorError


# Текст для перевода
def translate(text: str) -> str:
    headers = generate_random_headers()
    return ts.translate_text(
        text,
        from_language="en",
        to_language="ru",
        translator="yandex",
        headers=headers,
    )


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
]

accepts = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "application/json, text/javascript, */*; q=0.01",
    "*/*",
]

accept_languages = [
    "en-US,en;q=0.5",
    "ru-RU,ru;q=0.9,en;q=0.8",
    "fr-FR,fr;q=0.9,en;q=0.8",
]


# Генерация рандомных заголовков
def generate_random_headers():
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": random.choice(accepts),
        "Accept-Language": random.choice(accept_languages),
    }
    return headers
