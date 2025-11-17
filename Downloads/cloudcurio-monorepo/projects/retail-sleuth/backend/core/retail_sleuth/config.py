#!/usr/bin/env python3
'''Configuration loading for Retail Sleuth.'''

import os
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    dsn: str

@dataclass
class AppConfig:
    db: DatabaseConfig
    log_level: str = 'INFO'

def load_config() -> AppConfig:
    '''Load configuration from environment variables.'''
    dsn = os.getenv('RETAIL_SLEUTH_DB_DSN', 'postgresql://postgres:postgres@localhost:5432/retail_sleuth')
    log_level = os.getenv('RETAIL_SLEUTH_LOG_LEVEL', 'INFO')
    return AppConfig(db=DatabaseConfig(dsn=dsn), log_level=log_level)
