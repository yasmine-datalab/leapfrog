"""Student Db module"""

from typing import Annotated, Optional
from beanie import Indexed
from ..schemas import Student as StudentBase

from .document import DocumentBase


class Student(DocumentBase, StudentBase):
    """Student Db model"""

    user_id: Annotated[str, Indexed(unique=True)]

    @classmethod
    async def get_user_id(cls, user_id: str) -> Optional["Student"]:
        """Get student by user id."""

        return await cls.find_one(cls.user_id == user_id)

    class Settings:
        """Db Settings"""

        name = "student"
