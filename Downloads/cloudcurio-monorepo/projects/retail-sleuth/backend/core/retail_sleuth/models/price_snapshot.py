#!/usr/bin/env python3
'''Price snapshot model.'''

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class PriceSnapshot:
    '''Represents a single observation of an item's price at a point in time.'''
    item_id: uuid.UUID
    retailer_id: uuid.UUID
    price: float
    currency: str
    availability: Optional[str]
    collected_at: datetime
