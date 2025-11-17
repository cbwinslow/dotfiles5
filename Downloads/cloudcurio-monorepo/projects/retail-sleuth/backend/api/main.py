#!/usr/bin/env python3
'''FastAPI application for Retail Sleuth.'''

from fastapi import FastAPI, HTTPException
from typing import List
import uuid

from retail_sleuth.config import load_config
from retail_sleuth.logging_utils import setup_logging, get_logger

app = FastAPI(title='Retail Sleuth API')
cfg = load_config()
setup_logging(cfg.log_level)
log = get_logger(__name__)

# Placeholder in-memory store for demo
RETAILERS = []

@app.on_event('startup')
async def startup_event():
    log.info('Retail Sleuth API starting up')

@app.get('/health')
async def health():
    return {'status': 'ok'}

@app.get('/retailers/', response_model=List[dict])
async def list_retailers():
    return RETAILERS

@app.get('/retailers/{slug}', response_model=dict)
async def get_retailer(slug: str):
    for r in RETAILERS:
        if r.get('slug') == slug:
            return r
    raise HTTPException(status_code=404, detail='Retailer not found')
