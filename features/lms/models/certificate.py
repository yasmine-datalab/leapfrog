"""Certficate Db module"""

from beanie.odm.queries.find import FindMany
from schemas import Certificate as CertificateBase

from .document import DocumentBase


class Certificate(DocumentBase, CertificateBase):
    """Certificate Db model"""

    @classmethod
    def get_student_id(cls, student_id: str) -> FindMany["Certificate"]:
        """Get certificates by student id."""

        return cls.find(cls.student_id == student_id)

    class Settings:
        """Db Settings"""

        name = "certificate"
        indexes = [
            "student_id",
            "course_id",
            [("student_id", 1), ("course_id")],
        ]
