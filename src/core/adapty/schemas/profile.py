from .base import AdaptyObject
from .access_level import AdaptyAccessLevel
from .subscription import AdaptySubscription
from .non_subscription import AdaptyNonSubscription

from typing import Optional


class AdaptyProfile(AdaptyObject):
    """ User reference in the Adapty API """

    profile_id: str
    total_revenue_usd: float
    customer_user_id: Optional[str] = None
    paid_access_levels: Optional[dict[str, AdaptyAccessLevel]] = None
    subscriptions: Optional[dict[str, AdaptySubscription]] = None
    non_subscriptions: Optional[dict[str, AdaptyNonSubscription]] = None
    custom_attributes: Optional[dict[str, any]] = None


__all__ = (
    'AdaptyProfile',
)
