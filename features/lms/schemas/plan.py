"""Plan schemas module"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, UUID4


class BillingCycle(Enum):
    """Billing cycle enumerations"""

    MONTHLY = "monthly"
    ANNUALLY = "annually"


class PlanBase(BaseModel):
    """Plan Base model"""

    name: str
    description: str
    price: float
    billing_cycle: BillingCycle
    features: list[str]
    active: bool
    is_trial: bool


class PlanCreate(PlanBase):
    """Plan creattion model"""


class PlanUpdate(BaseModel):
    """Plan update model"""

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    billing_cycle: Optional[BillingCycle] = None
    features: list[Optional[str]] = None
    active: Optional[bool] = None


class Plan(PlanBase):
    """Subscription Plan Schema"""

    id: UUID4
    created_at: datetime
    updated_at: datetime
