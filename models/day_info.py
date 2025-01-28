from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from database.database import Base


class DayInfo(Base):
    __tablename__ = "day_info"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    moon_day: Mapped[str] = mapped_column(String(15), nullable=False)
    first_element_id: Mapped[int] = mapped_column(ForeignKey("elements.id"), nullable=False)
    first_element = relationship(
        "ElementModel",
        foreign_keys=[first_element_id],
        backref=backref("first_element", lazy='dynamic')
    )
    second_element_id: Mapped[int] = mapped_column(ForeignKey("elements.id"), nullable=False)
    second_element = relationship(
        "ElementModel",
        foreign_keys=[second_element_id],
        backref=backref("second_element", lazy='dynamic')
    )
    arch_id: Mapped[int] = mapped_column(ForeignKey("arch.id"), nullable=False)
    arch = relationship("ArchModel", backref=backref("arch", lazy='dynamic'))
    la_id: Mapped[int] = mapped_column(ForeignKey("la.id"), nullable=False)
    la = relationship("LaModel", backref=backref("la", lazy='dynamic'))
    yelam_id: Mapped[int] = mapped_column(ForeignKey("yelam.id"), nullable=False)
    yelam = relationship("YelamModel", backref=backref("yelam", lazy='dynamic'))
    haircutting_id: Mapped[int] = mapped_column(ForeignKey("haircutting.id"), nullable=False)
    haircutting = relationship("HaircuttingModel", backref=backref("haircutting", lazy='dynamic'))
    descriptions: Mapped[list["Description"]] = relationship("Description", back_populates="day_info")


class ElementModel(Base):
    init_data = [
        {"name": "Earth"},
        {"name": "Wind"},
        {"name": "Fire"},
        {"name": "Water"}
    ]
    __tablename__ = "elements"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)


class LaModel(Base):
    init_data = [
        {"moon_day": 1, "ru_name": "подошва стопы", "en_name": "sole of foot"},
        {"moon_day": 2, "ru_name": "лодыжки", "en_name": "ankles"},
        {"moon_day": 3, "ru_name": "медиальная сторона бедер", "en_name": "(medial side of) thighs"},
        {"moon_day": 4, "ru_name": "талия", "en_name": "waistline"},
        {"moon_day": 5, "ru_name": "внутренняя часть рта", "en_name": "(interior of) mouth"},
        {"moon_day": 6, "ru_name": "грудь", "en_name": "chest"},
        {"moon_day": 7, "ru_name": "спина", "en_name": "back"},
        {"moon_day": 8, "ru_name": "ладони рук", "en_name": "palms of hands"},
        {"moon_day": 9, "ru_name": "печень", "en_name": "liver"},
        {"moon_day": 10, "ru_name": "талия", "en_name": "waistline"},
        {"moon_day": 11, "ru_name": "нос", "en_name": "nose"},
        {"moon_day": 12, "ru_name": "живот", "en_name": "stomach"},
        {"moon_day": 13, "ru_name": "лопатки", "en_name": "shoulder blades"},
        {"moon_day": 14,
         "ru_name": "кровеносный сосуд над большими пальцами",
         "en_name": "blood vessel above thumbs"},
        {"moon_day": 15, "ru_name": "все тело", "en_name": "whole of body"},
        {"moon_day": 16, "ru_name": "шея", "en_name": "neck"},
        {"moon_day": 17, "ru_name": "горло", "en_name": "throat"},
        {"moon_day": 18, "ru_name": "подложечная ямка", "en_name": "pit of the stomach"},
        {"moon_day": 19, "ru_name": "лодыжки", "en_name": "ankles"},
        {"moon_day": 20, "ru_name": "подошва стопы", "en_name": "sole of foot"},
        {"moon_day": 21, 'ru_name': 'большой палец ноги', 'en_name': 'big toe'},
        {"moon_day": 22, 'ru_name': 'левая лопатка', 'en_name': 'left shoulder blade'},
        {"moon_day": 23, 'ru_name': 'печень', 'en_name': 'liver'},
        {"moon_day": 24, 'ru_name': 'ладони рук', 'en_name': 'palms of hands'},
        {"moon_day": 25, 'ru_name': 'язык', 'en_name': 'tongue'},
        {"moon_day": 26, 'ru_name': 'колени', 'en_name': 'knees'},
        {"moon_day": 27, 'ru_name': 'колени', 'en_name': 'knees'},
        {"moon_day": 28, 'ru_name': 'половые органы', 'en_name': 'sexual organs'},
        {"moon_day": 29, 'ru_name': 'зрачки', 'en_name': 'pupils'},
        {"moon_day": 30, 'ru_name': 'все тело', 'en_name': 'whole of body'}
    ]

    __tablename__ = "la"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(30), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(30), nullable=False)


class ArchModel(Base):
    init_data = [
        {"moon_day": 1, "name": "Don", "ru_desc": "Никого не приглашать", "en_desc": "Do not invite anyone"},
        {"moon_day": 2, "name": "Tshong", "ru_desc": "Не начинайте бизнес-проекты",
         "en_desc": "Do not start business ventures"},
        {"moon_day": 3, "name": "Pu", "ru_desc": "Не выводите младенца на улицу в первый раз",
         "en_desc": "Do not take your infant first time outside"},
        {"moon_day": 4, "name": "Mag", "ru_desc": "Не инициируйте никакую войну и связанную с ней работу",
         "en_desc": "Do not initiate any war and its related work"},
        {"moon_day": 5, "name": "Nyen", "ru_desc": "Не заводите новых сопровождающих",
         "en_desc": "Do not make any new accompany"},
        {"moon_day": 6, "name": "Khar", "ru_desc": "Не стройте и не начинайте никаких строительных работ",
         "en_desc": "Do not build and initiate any construction work"},
        {"moon_day": 7, "name": "Pag", "ru_desc": "Не вступайте в брак", "en_desc": "Do not marry"},
        {"moon_day": 8, "name": "Dur", "ru_desc": "Не проводите кремацию", "en_desc": "Do not make any cremation"},
        {"moon_day": 9, "name": "Shi", "ru_desc": "Не проводите поминки", "en_desc": "No memorials or wakes"},
        {"moon_day": 0, "name": "Chi", "ru_desc": "Не проводите никаких общественных мероприятий",
         "en_desc": "Do not make any community events"},
    ]

    __tablename__ = "arch"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    en_desc: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_desc: Mapped[str] = mapped_column(String(100), nullable=False)


class YelamModel(Base):
    init_data = [
        {"month": 1, "en_name": "South-West", "ru_name": "Юго-Запад"},
        {"month": 2, "en_name": "North", "ru_name": "Север"},
        {"month": 3, "en_name": "North-East", "ru_name": "Северо-Восток"},
        {"month": 4, "en_name": "South-East", "ru_name": "Юго-Восток"},
        {"month": 5, "en_name": "North-East", "ru_name": "Северо-Восток"},
        {"month": 6, "en_name": "West", "ru_name": "Запад"},
        {"month": 7, "en_name": "North-East", "ru_name": "Северо-Восток"},
        {"month": 8, "en_name": "South-East", "ru_name": "Юго-Восток"},
        {"month": 9, "en_name": "West", "ru_name": "Запад"},
        {"month": 10, "en_name": "South-East", "ru_name": "Юго-Восток"},
        {"month": 11, "en_name": "East", "ru_name": "Восток"},
        {"month": 12, "en_name": "North-East", "ru_name": "Северо-Восток"}
    ]
    __tablename__ = "yelam"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    month: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(30), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(30), nullable=False)


class HaircuttingModel(Base):
    init_data = [
        {"moon_day": 1, "ru_name": "Жизнь сокращается", "en_name": "Life is shortened", "is_inauspicious": False},
        {"moon_day": 2, "ru_name": "Болезни", "en_name": "Diseases", "is_inauspicious": False},
        {"moon_day": 3, "ru_name": "Богатство увеличивается", "en_name": "Wealth is increased",
         "is_inauspicious": True},
        {"moon_day": 4, "ru_name": "Сияние усиливается", "en_name": "Radiance is augmented", "is_inauspicious": True},
        {"moon_day": 5, "ru_name": "Приобретение большого богатства", "en_name": "Acquisition of great wealth",
         "is_inauspicious": True},
        {"moon_day": 6, "ru_name": "Сияние исчезает", "en_name": "Radiance disappears", "is_inauspicious": False},
        {"moon_day": 7, "ru_name": "Вовлеченность в судебные процессы, юридические проблемы",
         "en_name": "Entanglement in trials, legal problems", "is_inauspicious": False},
        {"moon_day": 8, "ru_name": "Долгая жизнь", "en_name": "Long life", "is_inauspicious": True},
        {"moon_day": 9, "ru_name": "Негативные встречи", "en_name": "Negative encounters", "is_inauspicious": False},
        {"moon_day": 10, "ru_name": "Достижение силы", "en_name": "Achievement of power", "is_inauspicious": True},
        {"moon_day": 11, "ru_name": "Достижение силы и интеллекта", "en_name": "Achievement of power and intelligence",
         "is_inauspicious": True},
        {"moon_day": 12, "ru_name": "Вредно для жизни", "en_name": "Detrimental to life", "is_inauspicious": False},
        {"moon_day": 13, "ru_name": "Богатство и счастье", "en_name": "Wealth and happiness", "is_inauspicious": True},
        {"moon_day": 14, "ru_name": "Изобилие материальных благ", "en_name": "Profuseness of material goods",
         "is_inauspicious": True},
        {"moon_day": 15,
         "ru_name": "Благоприятные предзнаменования, благоприятный",
         "en_name": "Favorable auguries, auspicious", "is_inauspicious": True},
        {"moon_day": 16, "ru_name": "Расширение Дхармы и потомства", "en_name": "Expansion of Dharma and of progeny",
         "is_inauspicious": True},
        {"moon_day": 17, "ru_name": "Кожа становится синюшной", "en_name": "The skin becomes bluish",
         "is_inauspicious": False},
        {"moon_day": 18, "ru_name": "Потеря всего богатства", "en_name": "Loss of all wealth",
         "is_inauspicious": False},
        {"moon_day": 19, "ru_name": "Долголетие и приумножение богатства",
         "en_name": "Longevity and increase of wealth", "is_inauspicious": True},
        {"moon_day": 20, "ru_name": "Красота", "en_name": "Beauty", "is_inauspicious": True},
        {"moon_day": 21, "ru_name": "Обретение великой силы", "en_name": "Attainment of great strength",
         "is_inauspicious": True},
        {"moon_day": 22, "ru_name": "Многочисленные болезни", "en_name": 'Numerous illnesses',
         "is_inauspicious": False},
        {"moon_day": 23, 'ru_name': 'Здоровье', 'en_name': 'Wealth', "is_inauspicious": True},
        {"moon_day": 24, 'ru_name': 'Инфекционные заболевания', 'en_name': 'Infectious diseases',
         "is_inauspicious": False},
        {"moon_day": 25, 'ru_name': 'Проблемы сглаза', 'en_name': 'Problems of evil eye', "is_inauspicious": False},
        {"moon_day": 26, 'ru_name': 'Самый благоприятный день, все виды благ',
         'en_name': 'Most auspicious day, all kind of benefits', "is_inauspicious": True},
        {"moon_day": 27, 'ru_name': 'Нейтральный', 'en_name': 'Neutral', "is_inauspicious": True},
        {"moon_day": 28, 'ru_name': 'Причина обид', 'en_name': 'Cause of hard feelings', "is_inauspicious": False},
        {"moon_day": 29, 'ru_name': 'Дьявол разбудит душу', 'en_name': 'The soul will be waken away by the devil',
         "is_inauspicious": False},
        {"moon_day": 30, 'ru_name': 'Встреча с собственным убийцей', 'en_name': 'Meeting one\'s own assassin',
         "is_inauspicious": False}
    ]

    __tablename__ = "haircutting"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    moon_day: Mapped[int] = mapped_column(nullable=False, unique=True)
    en_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ru_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_inauspicious: Mapped[bool] = mapped_column(nullable=False)


class Description(Base):
    __tablename__ = "descriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=True)
    day_info_id: Mapped[int] = mapped_column(ForeignKey("day_info.id"), nullable=False)
    day_info: Mapped[DayInfo] = relationship("DayInfo", back_populates="descriptions")
