from .base import AdaptyObject

from typing import Optional
from datetime import datetime


class AdaptyAccessLevel(AdaptyObject):
    """ Customer access level """

    id: str
    is_active: bool
    is_lifetime: bool
    will_renew: bool
    is_in_grace_period: bool
    vendor_product_id: Optional[str] = None
    base_plan_id: Optional[str] = None
    active_introductory_offer_type: Optional[str] = None
    active_promotional_offer_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    starts_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    renewed_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None
    billing_issue_detected_at: Optional[datetime] = None


__all__ = (
    'AdaptyAccessLevel',
)
