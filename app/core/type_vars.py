from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from database import BaseWithId

T = TypeVar("T", bound="BaseWithId")
