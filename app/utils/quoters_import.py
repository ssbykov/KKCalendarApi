import io
from typing import Sequence

import pandas as pd
from sqlalchemy import select

from app.database import db_helper, Quote, Lama
from app.database.crud.lamas import LamaRepository
from app.database.schemas.lama import LamaSchemaCreate
from app.database.schemas.quote import QuoteSchemaCreate

TASK_NAME = "tasks.process_import"


from collections import defaultdict
from difflib import SequenceMatcher


async def process_import(file_bytes: bytes) -> str:
    df = pd.read_excel(io.BytesIO(file_bytes))
    df = df.dropna(subset=["Author"])

    rejected_rows = []
    count = 0

    async for session in db_helper.get_session():
        lama_repo = LamaRepository(session)

        # Загружаем все цитаты с привязкой к автору
        result = await session.execute(select(Lama.id, Lama.name))
        lamas_in_base = result.all()
        existing_lamas = {name: id_ for id_, name in lamas_in_base}

        # Получаем все цитаты, сгруппированные по автору
        result = await session.execute(select(Quote.text, Lama.name).join(Lama))
        quotes_by_author: dict[str, list[str]] = defaultdict(list)
        for text, author_name in result.all():
            quotes_by_author[author_name].append(text)

        # Словарь для новых цитат по авторам
        new_quotes_by_author: dict[str, set[str]] = defaultdict(set)
        filtered_rows = []

        for row_number, (_, row) in enumerate(df.iterrows(), start=2):
            author = str(row["Author"]).strip()
            quote_text = str(row["Quote"]).strip()

            if is_quote_unique(
                quote=quote_text,
                existing=quotes_by_author.get(author, []),
                new_quotes=new_quotes_by_author[author],
            ):
                new_quotes_by_author[author].add(quote_text)
                filtered_rows.append(row)
            else:
                rejected_rows.append(row_number)

        unique_quotes_df = pd.DataFrame(filtered_rows)

        # Группируем и сохраняем
        if len(unique_quotes_df) > 0:
            grouped = unique_quotes_df.groupby("Author")

            for author, group in grouped:  # type:ignore
                author = str(author).strip()

                if author not in existing_lamas:
                    lama_obj = LamaSchemaCreate(name=author)
                    existing_lamas[author] = await lama_repo.add_lama(lama_obj)

                for _, row in group.iterrows():
                    quote_parts = str(row["Quote"]).split("\n")
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

    return f"Информация по последнему импорту: загружено: {count}, отклонено: {len(rejected_rows)} цитат."


def is_quote_unique(
    quote: str,
    existing: list[str] | Sequence[str],
    new_quotes: set[str],
    max_ratio: float = 0.75,
) -> bool:
    return not any(
        SequenceMatcher(None, q, quote).ratio() > max_ratio for q in existing
    ) and not any(
        SequenceMatcher(None, q, quote).ratio() > max_ratio for q in new_quotes
    )
