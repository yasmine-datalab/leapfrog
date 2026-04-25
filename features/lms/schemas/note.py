"""Note schema"""

from datetime import datetime

from pydantic import BaseModel, UUID4


class NoteBase(BaseModel):
    """Note base model"""

    content: str


class NoteCreate(NoteBase):
    """Note create class"""

    progress_id: UUID4


class Note(NoteBase):
    """Corse notes model"""

    id: UUID4
    progress_id: UUID4
    created_at: datetime
    updated_at: datetime


class NoteUpdate(BaseModel):
    """Note update model"""

    content: str
