#!/usr/bin/env python3
'''HTML-based client using crawl4ai (placeholder integration).'''

from typing import List

from ..logging_utils import get_logger
from ..models.item import Item
from ..models.price_snapshot import PriceSnapshot
from .base_client import BaseClient

log = get_logger(__name__)

class HtmlClient(BaseClient):
    '''Client that uses HTML crawling to retrieve data.'''

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def fetch_items(self) -> List[Item]:
        log.info('HtmlClient.fetch_items called (placeholder implementation)')
        return []

    def fetch_price_snapshots(self, items: List[Item]) -> List[PriceSnapshot]:
        log.info('HtmlClient.fetch_price_snapshots called (placeholder implementation)')
        return []
