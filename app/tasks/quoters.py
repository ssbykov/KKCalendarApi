import asyncio
import io
from difflib import SequenceMatcher
from typing import Sequence

from sqlalchemy import select

from app.celery_worker import celery_app
from app.database.crud.lamas import LamaRepository
from app.database import db_helper, Quote, Lama
from app.database.schemas.lama import LamaSchemaCreate
from app.database.schemas.quote import QuoteSchemaCreate
import pandas as pd


@celery_app.task(name="tasks.process_import")
def run_async(file_bytes: bytes):
    import asyncio
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(process_import(file_bytes))


async def process_import(file_bytes: bytes) -> str:

    df = pd.read_excel(io.BytesIO(file_bytes))

    # Удаляем строки с пустыми авторами
    df = df.dropna(subset=["Author"])

    rejected_rows = []
    count = 0
    async for session in db_helper.get_session():
        lama_repo = LamaRepository(session)

        # Получаем все существующие цитаты один раз
        result = await session.execute(select(Quote.text))
        quotes_in_base = result.scalars().all()

        # Получаем все Лам из базы за один раз
        result = await session.execute(select(Lama))
        lamas_in_base = result.scalars().all()

        # Создаем словарь для быстрого поиска авторов
        existing_lamas = {lama.name: lama.id for lama in lamas_in_base}  # type: ignore

        new_quotes_set: set[str] = set()

        # Отфильтрованные строки
        filtered_rows = []

        # Итерируем по строкам и отбираем уникальные
        for row_number, (_, row) in enumerate(df.iterrows(), start=2):
            quote_text = str(row["Quote"]).strip()
            if is_quote_unique(
                quote=quote_text,
                existing=quotes_in_base,
                new_quotes=new_quotes_set,
            ):
                new_quotes_set.add(quote_text)
                filtered_rows.append(row)
            else:
                rejected_rows.append(row_number)

        # Создаем новый DataFrame из отфильтрованных строк
        unique_quotes_df = pd.DataFrame(filtered_rows)

        # Группируем по авторам для эффективной вставки
        if len(unique_quotes_df) > 0:
            grouped = unique_quotes_df.groupby("Author")

            for author, group in grouped:
                if author not in existing_lamas:
                    lama_obj = LamaSchemaCreate(name=str(author))
                    existing_lamas[author] = await lama_repo.add_lama(lama_obj)

                for _, row in group.iterrows():
                    quote_parts = row["Quote"].split("\n")
                    if author in quote_parts[-1]:
                        new_quote = "".join(quote_parts[:-1]).strip()
                    else:
                        new_quote = row["Quote"].strip()
                    quote_obj = QuoteSchemaCreate(
                        lama_id=existing_lamas[author], text=new_quote
                    )
                    session.add(quote_obj.to_orm())
                    count += 1

            await session.commit()

    print(
        f"Импорт завершен. Загружено: {count}, пропущено: {len(rejected_rows)} строк."
    )
    return (
        f"Импорт завершен. Загружено: {count}, пропущено: {len(rejected_rows)} строк."
    )


def is_quote_unique(
    quote: str,
    existing: Sequence[str],
    new_quotes: set[str],
    max_ratio: float = 0.75,
) -> bool:

    return not any(
        SequenceMatcher(None, q, quote).ratio() > max_ratio for q in existing
    ) and not any(
        SequenceMatcher(None, q, quote).ratio() > max_ratio for q in new_quotes
    )
