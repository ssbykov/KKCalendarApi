from crud.mixines import GetBackNextIdMixin
from database.models import Emoji


class EmojiRepository(GetBackNextIdMixin[Emoji]):
    model = Emoji
