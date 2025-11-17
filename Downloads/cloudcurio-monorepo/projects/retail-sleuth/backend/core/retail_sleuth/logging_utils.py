#!/usr/bin/env python3
'''Logging utilities for Retail Sleuth.'''

import logging
from typing import Optional

def setup_logging(level: str = 'INFO') -> None:
    '''Configure root logger with a simple, structured format.'''
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )

def get_logger(name: Optional[str] = None) -> logging.Logger:
    '''Get a logger with the given name.'''
    return logging.getLogger(name or 'retail_sleuth')
