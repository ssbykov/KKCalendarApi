from database.crud.mixines import GetBackNextIdMixin
from database import Emoji


class EmojiRepository(GetBackNextIdMixin[Emoji]):
    model = Emoji
