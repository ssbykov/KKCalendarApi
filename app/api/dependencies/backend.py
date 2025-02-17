from fastapi_users.authentication import (
    AuthenticationBackend,
)

from api.dependencies.strategy import get_database_strategy
from core.auth.transport import bearer_transport

authentication_backend = AuthenticationBackend(
    name="access-token-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
