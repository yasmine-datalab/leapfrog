"""Document Model Base"""

from uuid import uuid4
from datetime import datetime
from pydantic import UUID4, Field
from beanie import Document


class DocumentBase(Document):
    """Document Base Db model"""

    id: UUID4 = Field(default_factory=uuid4, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        await super().save(*args, **kwargs)
