"""Student schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4


class StudentBase(BaseModel):
    """Student base model"""

    bio: Optional[str] = None
    goal: Optional[str] = None
    skills: Optional[list[str]] = []
    hobbies: Optional[list[str]] = []
    preference: Optional[list[str]] = []


class StudentCreate(StudentBase):
    """Student creation model"""

    user_id: Optional[str] = None


class StudentUpdate(StudentBase):
    """Student update model"""


class Student(StudentBase):
    """Student schema"""

    id: UUID4
    user_id: str
    created_at: datetime
    updated_at: datetime
