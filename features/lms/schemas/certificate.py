"""Certifcate schemas"""

from datetime import datetime
from pydantic import BaseModel, UUID4, HttpUrl


class CertificateBase(BaseModel):
    """Certificate base model"""

    student_id: UUID4
    course_id: UUID4
    file_url: HttpUrl


class CertificateCreate(CertificateBase):
    """Certficate create model"""


class Certificate(CertificateBase):
    """Certficate schema"""

    id: UUID4
    created_at: datetime
    updated_at: datetime
