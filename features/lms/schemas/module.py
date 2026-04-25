"""Module schemas"""

from typing import Optional, List

from datetime import datetime
from pydantic import BaseModel, UUID4

from .lesson import Lesson, LessonBase


class ModuleBase(BaseModel):
    """Module base model"""

    name: str
    description: Optional[str] = None
    order: int
    course_id: UUID4


class ModuleCreate(ModuleBase):
    """Module create model"""


class ModuleUpdate(BaseModel):
    """Module update model"""

    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None


class Module(ModuleBase):
    """Module read model"""

    id: UUID4
    lessons: List[Lesson]
    created_at: datetime
    updated_at: datetime


class ModuleProgram(ModuleBase):
    """Module Program model"""

    lessons: List[LessonBase]
