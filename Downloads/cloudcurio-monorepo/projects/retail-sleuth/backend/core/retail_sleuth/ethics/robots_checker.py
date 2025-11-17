#!/usr/bin/env python3
'''Robots.txt compliance helper.'''

import urllib.robotparser
from functools import lru_cache
from ..logging_utils import get_logger

log = get_logger(__name__)

@lru_cache(maxsize=128)
def _get_parser(robots_url: str) -> urllib.robotparser.RobotFileParser:
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except Exception as exc:
        log.warning('Failed to read robots.txt from %s: %s', robots_url, exc)
    return parser

def is_allowed(robots_url: str, user_agent: str, url: str) -> bool:
    '''Check whether the given url is allowed for the user_agent.'''
    parser = _get_parser(robots_url)
    allowed = parser.can_fetch(user_agent, url)
    if not allowed:
        log.info('Robots.txt disallows %s for UA=%s', url, user_agent)
    return allowed
