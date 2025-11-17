#!/usr/bin/env python3
'''Base client interfaces for data sources.'''

from abc import ABC, abstractmethod
from typing import List
from ..models.item import Item
from ..models.price_snapshot import PriceSnapshot

class BaseClient(ABC):
    '''Abstract base for retailer-specific clients.'''

    @abstractmethod
    def fetch_items(self) -> List[Item]:
        '''Fetch items metadata.'''
        raise NotImplementedError

    @abstractmethod
    def fetch_price_snapshots(self, items: List[Item]) -> List[PriceSnapshot]:
        '''Fetch price snapshots for a list of items.'''
        raise NotImplementedError
