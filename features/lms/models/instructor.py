"""Instructor Db module"""

from typing import Annotated, Optional
from beanie import Indexed
from schemas import Instructor as InstructorBase

from .document import DocumentBase


class Instructor(DocumentBase, InstructorBase):
    """Instructor Db model"""

    user_id: Annotated[str, Indexed(unique=True)]

    @classmethod
    async def get_user_id(cls, user_id: str) -> Optional["Instructor"]:
        """Get instructor by user id."""

        return await cls.find_one(cls.user_id == user_id)

    class Settings:
        """DB setting"""

        name = "instructor"
