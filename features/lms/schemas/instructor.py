"""Instructor schema"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4


class InstructorBase(BaseModel):
    """Instructor Base model"""

    bio: Optional[str] = None
    expertise: Optional[list[str]] = None


class InstructorCreate(InstructorBase):
    """Instructor creation model"""

    user_id: Optional[str] = None


class InstructorUpdate(InstructorBase):
    """Instructor Update model"""


class Instructor(InstructorBase):
    """Instructor schema"""

    id: UUID4
    user_id: str
    bio: Optional[str]
    expertise: Optional[list[str]]
    created_at: datetime
    updated_at: datetime
