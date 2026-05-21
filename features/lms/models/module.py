"""Module Item Db module"""

from typing import List
from beanie import Link
from beanie.odm.queries.find import FindMany
from ..schemas import Module as ModuleBase
from .lesson import Lesson

from .document import DocumentBase


class Module(DocumentBase, ModuleBase):
    """Module Db model"""

    lessons: List[Link[Lesson]] = []

    @classmethod
    def get_course_id(cls, course_id: str) -> FindMany["Module"]:
        """Get modules by course id."""

        return cls.find(cls.course_id == course_id)

    class Settings:
        """Db setting"""

        name = "module"
