#!/usr/bin/env python3
'''PostgreSQL repositories.'''

import uuid
from typing import List
import psycopg2
import psycopg2.extras

from ..logging_utils import get_logger
from ..models.retailer import Retailer
from ..models.item import Item
from ..models.price_snapshot import PriceSnapshot

log = get_logger(__name__)

class PostgresRepository:
    '''Repository for storing domain models in PostgreSQL.'''

    def __init__(self, dsn: str):
        self.dsn = dsn

    def _get_conn(self):
        return psycopg2.connect(self.dsn)

    def upsert_retailer(self, retailer: Retailer) -> None:
        '''Insert or update a retailer record.'''
        sql = '''
        INSERT INTO retailers (id, name, slug, base_url, robots_txt_url, strategy,
                               rate_limit_per_minute, created_at, updated_at)
        VALUES (%(id)s, %(name)s, %(slug)s, %(base_url)s, %(robots_txt_url)s,
                %(strategy)s, %(rate_limit_per_minute)s, %(created_at)s, %(updated_at)s)
        ON CONFLICT (slug) DO UPDATE SET
            name = EXCLUDED.name,
            base_url = EXCLUDED.base_url,
            robots_txt_url = EXCLUDED.robots_txt_url,
            strategy = EXCLUDED.strategy,
            rate_limit_per_minute = EXCLUDED.rate_limit_per_minute,
            updated_at = now();
        '''
        params = retailer.__dict__
        with self._get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()

    def insert_price_snapshots(self, snapshots: List[PriceSnapshot]) -> None:
        '''Bulk insert price snapshots.'''
        if not snapshots:
            return
        sql = '''
        INSERT INTO item_prices
            (item_id, retailer_id, price, currency, availability, collected_at)
        VALUES %s
        '''
        values = [
            (s.item_id, s.retailer_id, s.price, s.currency, s.availability, s.collected_at)
            for s in snapshots
        ]
        with self._get_conn() as conn, conn.cursor() as cur:
            psycopg2.extras.execute_values(cur, sql, values)
            conn.commit()
