#!/usr/bin/env python3
'''Item model.'''

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from .base import BaseModel

@dataclass
class Item(BaseModel):
    '''Represents a specific product offered by a retailer.'''
    retailer_id: uuid.UUID
    sku: Optional[str]
    name: str
    category: Optional[str]
    image_url: Optional[str]
    raw_metadata: Dict[str, Any] = field(default_factory=dict)
