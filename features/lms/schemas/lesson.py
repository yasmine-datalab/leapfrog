"""Lesson schemas"""

import json
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, HttpUrl, model_validator, field_validator


class LessonBase(BaseModel):
    """Lesson Base model"""

    name: str
    description: Optional[str] = None
    order: int
    duration: float
    content: str
    module_id: UUID4


class LessonCreate(LessonBase):
    """Lesson creation model"""

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


class LessonUpdate(BaseModel):
    """Lesson Update Model"""

    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    duration: Optional[float] = None
    content: Optional[str] = None

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


class Lesson(LessonBase):
    """Lesson schema"""

    id: UUID4
    course_id: UUID4
    video: Optional[HttpUrl] = None
    resources: Optional[List[HttpUrl]] = []
    created_at: datetime
    updated_at: datetime
