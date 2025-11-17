#!/usr/bin/env python3
'''Base domain models.'''

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class BaseModel:
    '''Base model with id and timestamps.'''
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    def touch(self) -> None:
        '''Update updated_at timestamp.'''
        self.updated_at = datetime.utcnow()
