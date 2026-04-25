"""Lesson Db module"""

from beanie.odm.queries.find import FindMany
from schemas import Lesson as LessonBase

from .document import DocumentBase


class Lesson(DocumentBase, LessonBase):
    """Lesson Db model"""

    @classmethod
    def get_module_id(cls, module_id: str) -> FindMany["Lesson"]:
        """Get lessons by module id."""

        return cls.find(cls.module_id == module_id)

    @classmethod
    def get_course_id(cls, course_id: str) -> FindMany["Lesson"]:
        """Get lessons by course id."""

        return cls.find(cls.course_id == course_id)

    class Settings:
        """Db Settings"""

        name = "lesson"
