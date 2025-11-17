#!/usr/bin/env python3
'''REST-based client using discovered API endpoints.'''

from typing import List
import requests

from ..logging_utils import get_logger
from ..models.item import Item
from ..models.price_snapshot import PriceSnapshot
from .base_client import BaseClient

log = get_logger(__name__)

class RestClient(BaseClient):
    '''Client that uses a catalog of API endpoints to retrieve data.'''

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def fetch_items(self) -> List[Item]:
        '''Stub implementation; to be specialized per retailer.'''
        log.info('fetch_items called on RestClient base stub')
        return []

    def fetch_price_snapshots(self, items: List[Item]) -> List[PriceSnapshot]:
        '''Stub implementation; to be specialized per retailer.'''
        log.info('fetch_price_snapshots called on RestClient base stub')
        return []
