"""Course schema"""

import json
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict

from pydantic import BaseModel, UUID4, model_validator, field_validator, HttpUrl

from .instructor import Instructor

# from .category import Category
from .module import Module, ModuleProgram
from .reviews import Review
from .note import Note


class Level(str, Enum):
    """Course level enumeration"""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class CourseBase(BaseModel):
    """Course base model"""

    title: str
    description: Optional[str] = None
    duration: float
    level: Level
    category: str


class   CourseCreate(CourseBase):
    """Course creation model"""

    # category_id: UUID4
    instructor_id: Optional[UUID4] = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        """Validate to json"""
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    @field_validator("*", check_fields=True, mode="before")
    @classmethod
    def convert_empty_string_to_none(cls, value):
        """Convert Empty string to None"""

        if isinstance(value, str) and value == "":
            return None
        return value


class CourseUpdate(BaseModel):
    """Course update model"""

    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID4] = None
    duration: Optional[float] = None
    level: Optional[Level] = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        """Validate to json"""
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    @field_validator("*", check_fields=True, mode="before")
    @classmethod
    def convert_empty_string_to_none(cls, value):
        """Convert Empty string to None"""

        if isinstance(value, str) and value == "":
            return None
        return value


class Course(CourseBase):
    """Course model"""

    id: UUID4
    image: HttpUrl | str
    video: Optional[HttpUrl] = None
    # category: Category
    instructor_id: UUID4
    instructor: Instructor
    modules: List[Module]
    rating: int | None = None
    reviews: Optional[List[Review]] = []
    created_at: datetime
    updated_at: datetime


class CourseProgram(Course):
    """Course program model"""

    modules: List[ModuleProgram]


class CourseProgressUpdate(BaseModel):
    """Course Progress update schema"""

    is_favoris: Optional[bool] = None
    is_archive: Optional[bool] = None


class CourseProgress(BaseModel):
    """Course Porgress schema"""

    id: UUID4
    student_id: UUID4
    course_id: UUID4
    course: Course
    is_favoris: bool = False
    is_archive: bool = False
    notes: Optional[List[Note]] = []
    completed_modules: List[UUID4] = []
    module_progress: Dict[UUID4, List[UUID4]] = {}
    current_module_id: Optional[UUID4] = None
    current_lesson_id: Optional[UUID4] = None
    last_accessed: Optional[datetime] = None
    end_date: Optional[datetime] = None
    overall_progress: float = 0.0
    created_at: datetime
    updated_at: datetime
