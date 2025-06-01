from app.database.crud.mixines import GetBackNextIdMixin
from app.database import Emoji


class EmojiRepository(GetBackNextIdMixin[Emoji]):
    model = Emoji
