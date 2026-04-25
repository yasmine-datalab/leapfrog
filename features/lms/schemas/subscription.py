"""Subscription schemas module"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, UUID4
from .plan import Plan


class SubscriptionStatus(Enum):
    """Subscription statuses"""

    ACTIVE = "Active"
    CANCELLED = "Cancelled"
    SUSPENDED = "Suspended"


class SubscriptionBase(BaseModel):
    """Base Subscription Model"""

    user_id: Optional[str] = None


class SubscriptionCreate(SubscriptionBase):
    """Model for creating a new subscription"""

    plan_id: UUID4


class SubscriptionUpdate(BaseModel):
    """Suscription update model"""

    status: Optional[SubscriptionStatus] = None
    plan_id: Optional[UUID4] = None
    cancel_resaon: Optional[str] = None


class Subscription(SubscriptionBase):
    """Full Subscription Schema"""

    id: UUID4
    user_id: str
    plan: Plan
    start_date: datetime
    end_date: datetime = None
    status: SubscriptionStatus
    renewal_date: Optional[datetime] = None
    cancel_resaon: Optional[str] = None
    created_at: datetime
    updated_at: datetime
