from .base import AdaptyObject

from typing import Optional
from datetime import datetime


class AdaptyNonSubscription(AdaptyObject):
    """ Non subscription purchase schema """

    purchase_id: str
    purchased_at: datetime
    is_one_time: bool
    is_sandbox: bool
    vendor_product_id: Optional[str] = None
    vendor_transaction_id: Optional[str] = None
    vendor_original_transaction_id: Optional[str] = None
    store: Optional[str] = None


__all__ = (
    'AdaptyNonSubscription',
)
