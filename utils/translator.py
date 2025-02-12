import random

import translators as ts  # type: ignore
from fake_headers import Headers


# Текст для перевода
def translate(text: str) -> str:
    headers = Headers().generate()
    try:
        translated_text = ts.translate_text(
            text,
            from_language="en",
            to_language="ru",
            translator="yandex",
            headers=headers,
        )
        if isinstance(translated_text, str):
            return translated_text
        else:
            return str(translated_text)  # Преобразуем в строку, если это необходимо
    except Exception as e:
        print(f"Translation failed: {e}")
        return text
