from app.database.crud.mixines import GetBackNextIdMixin
from app.database import Advertisement


class AdvertisementRepository(GetBackNextIdMixin[Advertisement]):
    model = Advertisement
