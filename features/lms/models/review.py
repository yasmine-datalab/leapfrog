"""Course review db module"""

from beanie.odm.queries.find import FindMany
from pydantic import UUID4
from ..schemas import Review as ReviewBase

from .document import DocumentBase


class Review(DocumentBase, ReviewBase):
    """Review Db model"""

    @classmethod
    def get_course_id(cls, course_id: UUID4) -> FindMany["Review"]:
        """Get reviews by course id."""

        return cls.find(
            cls.course_id == course_id,
        )

    class Settings:
        """Db settings"""

        name = "review"
        indexes = [
            "student_id",
            "course_id",
            [("student_id", 1), ("course_id")],
        ]
