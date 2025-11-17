#!/usr/bin/env python3
'''Retailer model.'''

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

from .base import BaseModel

@dataclass
class Retailer(BaseModel):
    '''Represents a retailer that can be crawled or queried via API.'''
    name: str
    slug: str
    base_url: str
    robots_txt_url: Optional[str]
    strategy: str
    rate_limit_per_minute: int

    @classmethod
    def new(cls, name: str, slug: str, base_url: str,
            robots_txt_url: Optional[str] = None,
            strategy: str = 'rest',
            rate_limit_per_minute: int = 30) -> 'Retailer':
        now = datetime.utcnow()
        return cls(
            id=uuid.uuid4(),
            created_at=now,
            updated_at=now,
            name=name,
            slug=slug,
            base_url=base_url,
            robots_txt_url=robots_txt_url,
            strategy=strategy,
            rate_limit_per_minute=rate_limit_per_minute,
        )
