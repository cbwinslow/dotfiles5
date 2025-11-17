#!/usr/bin/env python3
'''HTTP helper utilities.'''

from typing import Dict, Any, Optional
import requests

from ..logging_utils import get_logger

log = get_logger(__name__)

def get_json(url: str, timeout: int = 10, headers: Optional[Dict[str, str]] = None) -> Any:
    '''Perform a GET request and return parsed JSON, with basic error handling.'''
    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as exc:
        log.error('HTTP error on %s: %s', url, exc)
        raise
    except requests.exceptions.RequestException as exc:
        log.error('Request error on %s: %s', url, exc)
        raise
