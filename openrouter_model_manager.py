#!/usr/bin/env python3
"""
OpenRouter Free Model Discovery and Rotation System
Automatically discovers and manages free models with intelligent rotation
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    TESTING = "testing"

@dataclass
class ModelMetrics:
    """Performance metrics for a model"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    error_rate: float = 0.0
    
    def update_success(self, response_time: float):
        self.total_requests += 1
        self.successful_requests += 1
        self.last_success = datetime.now()
        self.consecutive_failures = 0
        
        # Update average response time
        if self.total_requests == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + response_time) 
                / self.total_requests
            )
        
        self._update_error_rate()
    
    def update_failure(self):
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure = datetime.now()
        self.consecutive_failures += 1
        self._update_error_rate()
    
    def _update_error_rate(self):
        if self.total_requests > 0:
            self.error_rate = self.failed_requests / self.total_requests

@dataclass
class FreeModel:
    """Represents a free model from OpenRouter"""
    id: str
    name: str
    description: str
    context_length: int
    pricing: Dict[str, float]
    status: ModelStatus = ModelStatus.AVAILABLE
    metrics: ModelMetrics = field(default_factory=ModelMetrics)
    last_checked: Optional[datetime] = None
    rate_limit_rpm: Optional[int] = None
    
    @property
    def is_free(self) -> bool:
        """Check if model is actually free"""
        return (self.pricing.get("prompt", 0) == 0 and 
                self.pricing.get("completion", 0) == 0)
    
    @property
    def health_score(self) -> float:
        """Calculate health score for model selection"""
        if self.status == ModelStatus.UNAVAILABLE:
            return 0.0
        
        # Base score from success rate
        success_rate = 1.0 - self.metrics.error_rate
        
        # Penalty for consecutive failures
        failure_penalty = min(0.5, self.metrics.consecutive_failures * 0.1)
        
        # Bonus for recent successes
        time_bonus = 0.0
        if self.metrics.last_success:
            time_since_success = (datetime.now() - self.metrics.last_success).total_seconds()
            time_bonus = max(0, 0.2 * (1 - time_since_success / 3600))  # Decay over hour
        
        # Penalty for slow response times
        speed_penalty = min(0.3, max(0, (self.metrics.average_response_time - 2.0) * 0.1))
        
        score = success_rate - failure_penalty + time_bonus - speed_penalty
        return max(0.0, min(1.0, score))

class OpenRouterModelManager:
    """Manages discovery and rotation of free OpenRouter models"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.models: Dict[str, FreeModel] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_discovery: Optional[datetime] = None
        self.discovery_interval = timedelta(hours=1)  # Refresh every hour
        self.health_check_interval = timedelta(minutes=5)  # Health check every 5 minutes
        self.circuit_breaker_threshold = 5  # Failures before circuit breaker
        self.rate_limit_tracker: Dict[str, List[datetime]] = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.discover_free_models()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def discover_free_models(self) -> List[FreeModel]:
        """Discover all free models from OpenRouter API"""
        logger.info("Discovering free models from OpenRouter...")
        
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        url = "https://openrouter.ai/api/v1/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch models: {response.status}")
                    return []
                
                data = await response.json()
                free_models = []
                
                for model_data in data.get("data", []):
                    model = FreeModel(
                        id=model_data["id"],
                        name=model_data["name"],
                        description=model_data.get("description", ""),
                        context_length=model_data.get("context_length", 0),
                        pricing=model_data.get("pricing", {})
                    )
                    
                    if model.is_free:
                        self.models[model.id] = model
                        free_models.append(model)
                        logger.info(f"Found free model: {model.name} ({model.id})")
                
                self.last_discovery = datetime.now()
                logger.info(f"Discovered {len(free_models)} free models")
                return free_models
                
        except Exception as e:
            logger.error(f"Error discovering models: {e}")
            return []
    
    async def get_best_model(self, exclude_models: Optional[Set[str]] = None) -> Optional[FreeModel]:
        """Get the best available model based on health score"""
        await self._refresh_if_needed()
        
        available_models = [
            model for model in self.models.values()
            if (model.status == ModelStatus.AVAILABLE and
                (not exclude_models or model.id not in exclude_models))
        ]
        
        if not available_models:
            logger.warning("No available models")
            return None
        
        # Sort by health score
        best_model = max(available_models, key=lambda m: m.health_score)
        logger.info(f"Selected best model: {best_model.name} (score: {best_model.health_score:.2f})")
        return best_model
    
    async def rotate_model(self, current_model_id: str) -> Optional[FreeModel]:
        """Rotate to next best model"""
        logger.info(f"Rotating from model: {current_model_id}")
        return await self.get_best_model(exclude_models={current_model_id})
    
    async def test_model_health(self, model_id: str) -> bool:
        """Test if a model is healthy and responsive"""
        if model_id not in self.models:
            return False
        
        model = self.models[model_id]
        model.status = ModelStatus.TESTING
        
        try:
            start_time = time.time()
            
            # Simple test request
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            }
            
            async with self.session.post(url, headers=headers, json=payload, timeout=10) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    model.metrics.update_success(response_time)
                    model.status = ModelStatus.AVAILABLE
                    logger.info(f"Model {model.name} is healthy (response time: {response_time:.2f}s)")
                    return True
                else:
                    model.metrics.update_failure()
                    model.status = ModelStatus.ERROR if response.status >= 500 else ModelStatus.RATE_LIMITED
                    logger.warning(f"Model {model.name} returned status {response.status}")
                    return False
                    
        except asyncio.TimeoutError:
            model.metrics.update_failure()
            model.status = ModelStatus.ERROR
            logger.warning(f"Model {model.name} timed out")
            return False
        except Exception as e:
            model.metrics.update_failure()
            model.status = ModelStatus.ERROR
            logger.error(f"Error testing model {model.name}: {e}")
            return False
    
    async def check_rate_limits(self, model_id: str) -> bool:
        """Check if model is rate limited"""
        now = datetime.now()
        if model_id not in self.rate_limit_tracker:
            self.rate_limit_tracker[model_id] = []
        
        # Clean old requests (older than 1 minute)
        self.rate_limit_tracker[model_id] = [
            req_time for req_time in self.rate_limit_tracker[model_id]
            if (now - req_time).total_seconds() < 60
        ]
        
        model = self.models.get(model_id)
        if model and model.rate_limit_rpm:
            requests_per_minute = len(self.rate_limit_tracker[model_id])
            if requests_per_minute >= model.rate_limit_rpm:
                model.status = ModelStatus.RATE_LIMITED
                return False
        
        return True
    
    async def record_request(self, model_id: str, success: bool, response_time: Optional[float] = None):
        """Record a request outcome for metrics"""
        if model_id not in self.models:
            return
        
        model = self.models[model_id]
        
        # Track for rate limiting
        now = datetime.now()
        if model_id not in self.rate_limit_tracker:
            self.rate_limit_tracker[model_id] = []
        self.rate_limit_tracker[model_id].append(now)
        
        # Update metrics
        if success and response_time is not None:
            model.metrics.update_success(response_time)
            if model.status != ModelStatus.AVAILABLE:
                model.status = ModelStatus.AVAILABLE
        else:
            model.metrics.update_failure()
            
            # Circuit breaker logic
            if model.metrics.consecutive_failures >= self.circuit_breaker_threshold:
                model.status = ModelStatus.UNAVAILABLE
                logger.warning(f"Circuit breaker activated for model {model.name}")
    
    async def _refresh_if_needed(self):
        """Refresh model list if discovery interval has passed"""
        if (not self.last_discovery or 
            datetime.now() - self.last_discovery > self.discovery_interval):
            await self.discover_free_models()
    
    async def health_check_loop(self):
        """Background loop to check model health"""
        while True:
            try:
                logger.info("Running health check on all models...")
                
                for model_id in list(self.models.keys()):
                    if self.models[model_id].status in [ModelStatus.AVAILABLE, ModelStatus.ERROR]:
                        await self.test_model_health(model_id)
                
                await asyncio.sleep(self.health_check_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def get_model_stats(self) -> Dict[str, Dict]:
        """Get statistics for all models"""
        stats = {}
        for model_id, model in self.models.items():
            stats[model_id] = {
                "name": model.name,
                "status": model.status.value,
                "health_score": model.health_score,
                "total_requests": model.metrics.total_requests,
                "success_rate": 1.0 - model.metrics.error_rate,
                "average_response_time": model.metrics.average_response_time,
                "consecutive_failures": model.metrics.consecutive_failures
            }
        return stats

# Example usage
async def main():
    """Demonstrate the model manager"""
    api_key = "your-openrouter-api-key"  # Replace with actual key
    
    async with OpenRouterModelManager(api_key) as manager:
        # Discover free models
        models = await manager.discover_free_models()
        print(f"Found {len(models)} free models")
        
        # Get best model
        best_model = await manager.get_best_model()
        if best_model:
            print(f"Best model: {best_model.name}")
        
        # Test a model
        if models:
            await manager.test_model_health(models[0].id)
        
        # Get statistics
        stats = manager.get_model_stats()
        print("\nModel Statistics:")
        for model_id, stat in stats.items():
            print(f"{stat['name']}: {stat['status']} (score: {stat['health_score']:.2f})")

if __name__ == "__main__":
    asyncio.run(main())