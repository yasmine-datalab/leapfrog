"""Course Taxonomy"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4


class CategoryBase(BaseModel):
    """Category base model"""

    name: str
    description: str


class CategoxyCreate(CategoryBase):
    """Course category creattion model"""


class CategoryUpdate(BaseModel):
    """Category update model"""

    name: Optional[str] = None
    description: Optional[str] = None


class Category(CategoryBase):
    """Category schema"""

    id: UUID4
    # subcatergory(eventually)
    created_at: datetime
    updated_at: datetime
