"""Course Review schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4


class ReviewBase(BaseModel):
    """Course review base model"""

    course_id: UUID4
    rating: int
    comment: str


class ReviewCreate(ReviewBase):
    """Course Review Creation model"""


class ReviewUpdate(BaseModel):
    """Course review update model"""

    rating: Optional[int] = None
    comment: Optional[str] = None


class Review(ReviewCreate):
    """Course review schema"""

    id: UUID4
    student_id: UUID4
    created_at: datetime
    updated_at: datetime
