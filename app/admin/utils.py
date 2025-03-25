from starlette.requests import Request


def check_superuser(request: Request) -> bool:
    return bool(request.session.get("user", {}).get("is_superuser"))
