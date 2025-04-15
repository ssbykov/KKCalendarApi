import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core import settings
from crud.days_info import DayInfoRepository
from crud.events import EventRepository
from database import SessionDep, db_helper
from database.schemas import DayInfoSchemaCreate, EventSchemaCreate
from utils.translator import translate

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class GoogleCalendarParser:
    HOST = "https://www.karmakagyucalendar.org/current-calendar"
    MONTHS_TAG = "CjVfdc"
    DAY_TAG = "n8H08c UVNKR"
    URL_PATTERN = r"➡️ [^\s]+|🌐 [^\s]+|https?://[^\s]+"
    FILTER_WORDS = (
        "🌑",
        "🌕",
        "100x",
        "1000x",
        "10000x",
        "100000x",
        "1000000x",
        "10000000x",
    )

    def __init__(self, session: SessionDep):
        self.calendar_id = settings.calendar.calendar_id
        account_info = json.loads(settings.calendar.secret_file)
        self.creds = service_account.Credentials.from_service_account_info(
            account_info, scopes=SCOPES
        )  # type: ignore
        self.service = build("calendar", "v3", credentials=self.creds)
        self.day_info_repo = DayInfoRepository(session)
        self.event_repo = EventRepository(session)

    async def load_events(self, year: int, month: int, period: int = 1) -> None:
        calendar_days_info = await self._calendar_request(year, month, period)
        days_info = []
        events_for_translate = {}
        for day in calendar_days_info:
            descriptions = day.get("description").split("\n\n")
            body_events = []
            for index, value in enumerate(descriptions):
                if "ELEMENTAL COMBINATION" in value:
                    body_events.extend(descriptions[:index])
                    break
            summary = day.get("summary").split(" ⋅ ")
            head_events = summary[1:-5].copy()

            parsed_events = self._events_filter(head_events, body_events)

            user_id = 6
            events = []
            for event in parsed_events:
                for duchen in (
                    "Chötrül Düchen",
                    "Saga Dawa Düchen",
                    "Chökhor Düchen",
                    "Lha Bab Düchen",
                ):
                    if duchen in event["name"]:
                        event["name"] = duchen
                        break
                event_in_base = await self.event_repo.get_event_by_name(event["name"])
                if event_in_base:
                    events.append(event_in_base.id)
                else:
                    ru_text = translate(event["text"]) if event["text"] else ""
                    event_schema = EventSchemaCreate(
                        name=event["name"],
                        en_name=event["name"],
                        en_text=event["text"],
                        ru_name=event["name"],
                        ru_text=ru_text,
                        link=event["link"],
                        user_id=int(user_id) if user_id else None,
                    )
                    new_event_id = await self.event_repo.add_event(event_schema)
                    events_for_translate[new_event_id] = event["name"]
                    events.append(new_event_id)

            moon, moon_day = summary[0].strip(".").split(".")
            elements = await self.day_info_repo.get_elements_by_name(summary[-5])
            arch_id = await self.day_info_repo.get_arch_id(moon_day)
            la_id = await self.day_info_repo.get_la_id(int(moon_day))
            haircutting_id = await self.day_info_repo.get_haircutting_day_id(
                int(moon_day)
            )
            yelam_id = await self.day_info_repo.get_yelam_day_id(moon)

            day_info = DayInfoSchemaCreate(
                date=day.get("start").get("date"),
                moon_day=f"{moon_day}.{moon}",
                elements_id=elements.id,
                arch_id=arch_id,
                la_id=la_id,
                yelam_id=yelam_id,
                haircutting_id=haircutting_id,
                events=events,
            )
            days_info.append(day_info)
        translated_events = translate("|".join(events_for_translate.values())).split(
            "|"
        )
        for event_id, ru_name in zip(events_for_translate.keys(), translated_events):
            await self.event_repo.ru_name_event_update(event_id, ru_name)

        await self.day_info_repo.add_days(days_info)

    async def _calendar_request(self, year: int, month: int, period: int = 1) -> Any:
        start_of_month = (
            datetime(year, month, 1).isoformat() + "Z"
        )  # 'Z' указывает на время UTC
        add_year = (month + period) // 12
        new_month = (month + period) % 12
        end_of_month = datetime(year + add_year, new_month, 1).isoformat() + "Z"

        try:
            days_info_result = (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=start_of_month,
                    timeMax=end_of_month,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            return days_info_result.get("items", [])[:-1]
        except HttpError as error:
            logging.error(f"An error occurred: {error}")
            return []

    def _events_filter(
        self, head_events: list[str], body_events: list[str]
    ) -> list[dict[str, str]]:
        events: list[dict[str, str]] = []
        buffer_body_events = body_events.copy()
        len_body_events = len(body_events)
        for head_event in head_events:
            if head_event not in self.FILTER_WORDS:
                event = {"name": head_event, "text": "", "link": ""}
                for idx, body_event in enumerate(body_events):
                    if head_event in body_event:
                        if body_event.startswith(head_event):
                            event["text"] = (
                                body_event.lstrip(head_event).lstrip(".:").strip()
                            )
                        else:
                            event["text"] = body_event
                        ext_events = []
                        if buffer_idx := buffer_body_events.index(body_event):
                            if events:
                                ext_events = buffer_body_events[:buffer_idx]
                                events[-1]["text"] += "\n" + "\n".join(ext_events)
                        buffer_body_events = body_events.copy()[idx + 1 :]
                        for ext_event in ext_events:
                            body_events.remove(ext_event)
                        body_events.remove(body_event)
                        break
                events.append(event)

        if buffer_body_events and len(buffer_body_events) != len_body_events:
            if events:
                events[-1]["text"] += "\n" + "\n".join(buffer_body_events)
                for buffer_body_event in buffer_body_events:
                    body_events.remove(buffer_body_event)

        for body_event in body_events:
            events.append({"name": body_event, "text": "", "link": ""})

        return self._parse_links(events)

    def _parse_links(self, events: list[dict[str, str]]) -> list[dict[str, str]]:
        for event in events:
            if not (text := event.get("text")):
                continue

            lines = text.split("\n")
            if matches := re.findall(self.URL_PATTERN, text):
                last_match = matches[-1]
                if last_match in lines[-1]:
                    lines.pop(-1)
                last_match = last_match.strip(r"➡️ 🌐")
                if not last_match.startswith("http"):
                    last_match = "http://" + last_match
                event["link"] = last_match

            cleaned_text = "\n".join(line for line in lines if line.strip())
            event["text"] = cleaned_text

        return events


async def main() -> None:
    async for session in db_helper.get_session():
        parser = GoogleCalendarParser(session)
        await parser.load_events(2025, 4, 9)


if __name__ == "__main__":
    asyncio.run(main())
