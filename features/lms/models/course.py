"""Course Db module"""

from typing import List, Optional
from beanie import Link, after_event, Delete
from beanie.odm.queries.find import FindMany
from pydantic import UUID4

from schemas import (
    Course as CourseBase,
    CourseProgress as CourseProgressBase,
)

from .module import Module
from .review import Review
from .instructor import Instructor
from .note import Note

from .document import DocumentBase


class Course(DocumentBase, CourseBase):
    """Course Db model"""

    modules: List[Link[Module]] = []
    reviews: List[Link[Review]] = []
    instructor: Link[Instructor]

    @after_event(Delete)
    async def delete_linked_documents(self):
        """Deletes linked Modules and Reviews, but keeps Instructor."""

        try:
            # Delete linked Modules
            for module_link in self.modules:
                module = await module_link.fetch()
                await module.delete()

            # Delete linked Reviews
            for review_link in self.reviews:
                review = await review_link.fetch()
                await review.delete()

            print("Deleted linked Modules and Reviews")
        # pylint: disable=W0718
        except Exception as e:
            print("Error deleting linked documents:  %s", e)

    @classmethod
    def get_instuctor_id(cls, instructor_id: str) -> FindMany["Course"]:
        """Get courses by instructor id."""

        return cls.find(cls.instructor_id == instructor_id, fetch_links=True)

    @classmethod
    def get_category_id(cls, category_id: str) -> FindMany["Course"]:
        """Get courses by category id."""

        return cls.find(cls.category.id == category_id, fetch_links=True)

    class Settings:
        """Database setting"""

        name = "course"


class CourseProgress(DocumentBase, CourseProgressBase):
    """Student course progress Db model"""

    course: Link[Course]
    notes: List[Link[Note]]

    @classmethod
    async def get_course_student_id(
        cls, student_id: UUID4, course_id: UUID4
    ) -> Optional["CourseProgress"]:
        """Get a course by student id."""

        return await cls.find_one(
            cls.student_id == student_id, cls.course_id == course_id, fetch_links=True
        )

    @classmethod
    def get_all_courses_student_id(
        cls, student_id: UUID4
    ) -> FindMany["CourseProgress"]:
        """Get courses by student id."""

        return cls.find(cls.student_id == student_id, fetch_links=True)

    class Settings:
        """Db setting"""

        name = "course_progress"
        indexes = [
            "student_id",
            "course_id",
            [("student_id", 1), ("course_id")],
        ]
