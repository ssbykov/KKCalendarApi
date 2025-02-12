from sqladmin import Admin

from admin.model_views import EventAdmin, DayInfoAdmin
from database import db_helper, Event


def init_admin(app):
    admin = Admin(app, db_helper.engine)
    admin.add_view(DayInfoAdmin)
    admin.add_view(EventAdmin)
