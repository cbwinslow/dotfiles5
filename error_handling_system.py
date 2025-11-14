#!/usr/bin/env python3
"""
Comprehensive Error Handling and Circuit Breaker System
Provides robust error recovery and fault tolerance for multi-agent systems
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import traceback
from functools import wraps
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, blocking calls
    HALF_OPEN = "half_open"  # Testing if service has recovered

@dataclass
class ErrorMetrics:
    """Metrics for tracking errors"""
    total_errors: int = 0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    errors_by_severity: Dict[ErrorSeverity, int] = field(default_factory=dict)
    last_error: Optional[datetime] = None
    consecutive_errors: int = 0
    recovery_attempts: int = 0
    successful_recoveries: int = 0
    
    def record_error(self, error_type: str, severity: ErrorSeverity):
        self.total_errors += 1
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
        self.errors_by_severity[severity] = self.errors_by_severity.get(severity, 0) + 1
        self.last_error = datetime.now()
        self.consecutive_errors += 1
    
    def record_success(self):
        self.consecutive_errors = 0
        self.successful_recoveries += 1
    
    def get_error_rate(self, time_window: timedelta, total_requests: int) -> float:
        """Calculate error rate in given time window"""
        if total_requests == 0:
            return 0.0
        return self.total_errors / total_requests

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: timedelta = timedelta(seconds=60)  # Time to wait before trying again
    success_threshold: int = 3          # Successes to close circuit
    monitoring_period: timedelta = timedelta(minutes=5)   # Period to monitor
    half_open_max_calls: int = 3        # Max calls in half-open state

class CircuitBreaker:
    """Implements circuit breaker pattern for fault tolerance"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self.metrics = ErrorMetrics()
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.config.half_open_max_calls:
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} half-open limit exceeded")
            self.half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(type(e).__name__)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset"""
        return (self.last_failure_time and 
                datetime.now() - self.last_failure_time >= self.config.recovery_timeout)
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"Circuit breaker {self.name} CLOSED - service recovered")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)
        
        self.metrics.record_success()
    
    def _on_failure(self, error_type: str):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        # Determine severity based on error type
        severity = self._classify_error(error_type)
        self.metrics.record_error(error_type, severity)
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.success_count = 0
            logger.warning(f"Circuit breaker {self.name} OPEN - failure in half-open state")
        elif (self.state == CircuitState.CLOSED and 
              self.failure_count >= self.config.failure_threshold):
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker {self.name} OPEN - threshold reached")
    
    def _classify_error(self, error_type: str) -> ErrorSeverity:
        """Classify error severity based on type"""
        critical_errors = {'ConnectionError', 'TimeoutError', 'CircuitBreakerOpenError'}
        high_errors = {'APIError', 'AuthenticationError', 'RateLimitError'}
        medium_errors = {'ValidationError', 'NotFoundError'}
        
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        elif error_type in high_errors:
            return ErrorSeverity.HIGH
        elif error_type in medium_errors:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "metrics": {
                "total_errors": self.metrics.total_errors,
                "consecutive_errors": self.metrics.consecutive_errors,
                "successful_recoveries": self.metrics.successful_recoveries
            }
        }

class RetryPolicy:
    """Implements various retry strategies"""
    
    def __init__(self, 
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 backoff_factor: float = 2.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt"""
        delay = min(self.base_delay * (self.backoff_factor ** (attempt - 1)), self.max_delay)
        
        if self.jitter:
            # Add random jitter to avoid thundering herd
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_attempts:
                    logger.error(f"Final attempt failed for {func.__name__}: {e}")
                    break
                
                delay = self.get_delay(attempt)
                logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
                await asyncio.sleep(delay)
        
        raise last_exception

class ErrorRecoveryManager:
    """Manages error recovery strategies"""
    
    def __init__(self):
        self.recovery_strategies: Dict[str, Callable] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.global_metrics = ErrorMetrics()
        
    def register_circuit_breaker(self, name: str, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Register a circuit breaker"""
        cb = CircuitBreaker(name, config)
        self.circuit_breakers[name] = cb
        return cb
    
    def register_retry_policy(self, name: str, policy: RetryPolicy):
        """Register a retry policy"""
        self.retry_policies[name] = policy
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register a recovery strategy for specific error type"""
        self.recovery_strategies[error_type] = strategy
    
    async def execute_with_protection(self, 
                                    func: Callable,
                                    circuit_breaker_name: Optional[str] = None,
                                    retry_policy_name: Optional[str] = None,
                                    *args, **kwargs) -> Any:
        """Execute function with all protections"""
        
        # Apply retry policy if specified
        if retry_policy_name and retry_policy_name in self.retry_policies:
            retry_policy = self.retry_policies[retry_policy_name]
            func_to_call = lambda: self._execute_with_circuit_breaker(func, circuit_breaker_name, *args, **kwargs)
            return await retry_policy.execute(func_to_call)
        else:
            return await self._execute_with_circuit_breaker(func, circuit_breaker_name, *args, **kwargs)
    
    async def _execute_with_circuit_breaker(self, 
                                          func: Callable,
                                          circuit_breaker_name: Optional[str],
                                          *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if circuit_breaker_name and circuit_breaker_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[circuit_breaker_name]
            return await circuit_breaker.call(func, *args, **kwargs)
        else:
            return await func(*args, **kwargs)
    
    async def attempt_recovery(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt to recover from error using registered strategies"""
        error_type = type(error).__name__
        
        if error_type in self.recovery_strategies:
            try:
                strategy = self.recovery_strategies[error_type]
                result = await strategy(error, context)
                if result:
                    logger.info(f"Recovery successful for {error_type}")
                    return True
            except Exception as recovery_error:
                logger.error(f"Recovery strategy failed for {error_type}: {recovery_error}")
        
        return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        total_circuit_breakers = len(self.circuit_breakers)
        open_circuit_breakers = sum(
            1 for cb in self.circuit_breakers.values() 
            if cb.state == CircuitState.OPEN
        )
        
        return {
            "total_errors": self.global_metrics.total_errors,
            "consecutive_errors": self.global_metrics.consecutive_errors,
            "circuit_breakers": {
                "total": total_circuit_breakers,
                "open": open_circuit_breakers,
                "closed": total_circuit_breakers - open_circuit_breakers
            },
            "circuit_breaker_details": {
                name: cb.get_status() 
                for name, cb in self.circuit_breakers.items()
            }
        }

# Decorators for easy integration
def with_circuit_breaker(circuit_breaker_name: str, recovery_manager: ErrorRecoveryManager):
    """Decorator to add circuit breaker protection"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await recovery_manager.execute_with_protection(
                func, circuit_breaker_name, None, *args, **kwargs
            )
        return wrapper
    return decorator

def with_retry(retry_policy_name: str, recovery_manager: ErrorRecoveryManager):
    """Decorator to add retry protection"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await recovery_manager.execute_with_protection(
                func, None, retry_policy_name, *args, **kwargs
            )
        return wrapper
    return decorator

def with_full_protection(circuit_breaker_name: str, 
                        retry_policy_name: str,
                        recovery_manager: ErrorRecoveryManager):
    """Decorator to add both circuit breaker and retry protection"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await recovery_manager.execute_with_protection(
                func, circuit_breaker_name, retry_policy_name, *args, **kwargs
            )
        return wrapper
    return decorator

# Custom exceptions
class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

class RecoveryFailedError(Exception):
    """Raised when recovery strategy fails"""
    pass

# Example recovery strategies
async def default_timeout_recovery(error: Exception, context: Dict[str, Any]) -> bool:
    """Default recovery for timeout errors"""
    logger.info("Attempting timeout recovery: waiting and retrying with longer timeout")
    await asyncio.sleep(5)  # Wait for service to recover
    return True

async def default_rate_limit_recovery(error: Exception, context: Dict[str, Any]) -> bool:
    """Default recovery for rate limit errors"""
    logger.info("Attempting rate limit recovery: exponential backoff")
    await asyncio.sleep(60)  # Wait longer for rate limit to reset
    return True

# Example usage
async def example_failing_service(should_fail: bool = False):
    """Example service that can fail"""
    if should_fail:
        raise ConnectionError("Service unavailable")
    return "Success"

async def main():
    """Demonstrate error handling system"""
    # Initialize recovery manager
    recovery_manager = ErrorRecoveryManager()
    
    # Register circuit breaker
    cb_config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=timedelta(seconds=10)
    )
    recovery_manager.register_circuit_breaker("example_service", cb_config)
    
    # Register retry policy
    retry_policy = RetryPolicy(max_attempts=3, base_delay=1.0)
    recovery_manager.register_retry_policy("default_retry", retry_policy)
    
    # Register recovery strategies
    recovery_manager.register_recovery_strategy("ConnectionError", default_timeout_recovery)
    recovery_manager.register_recovery_strategy("RateLimitError", default_rate_limit_recovery)
    
    # Test the system
    print("Testing error handling system...")
    
    try:
        # This should work
        result = await recovery_manager.execute_with_protection(
            example_failing_service, "example_service", "default_retry", False
        )
        print(f"Success: {result}")
        
        # This should trigger circuit breaker after multiple failures
        for i in range(5):
            try:
                result = await recovery_manager.execute_with_protection(
                    example_failing_service, "example_service", "default_retry", True
                )
                print(f"Unexpected success: {result}")
            except CircuitBreakerOpenError:
                print(f"Circuit breaker opened on attempt {i+1}")
                break
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
    
    finally:
        # Print system health
        health = recovery_manager.get_system_health()
        print("\nSystem Health:")
        print(json.dumps(health, indent=2))

if __name__ == "__main__":
    asyncio.run(main())