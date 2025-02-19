from fastapi_users.authentication import BearerTransport

from core import settings

bearer_transport = BearerTransport(tokenUrl=settings.api.token_url)
