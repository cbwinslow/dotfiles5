# Error Handling and Resilience Rules

**Priority:** High
**Applies To:** All AI agents
**Last Updated:** 2025-11-12
**Updated By:** System

## Rules

1. **Error Prevention**
   - Validate inputs before processing
   - Check preconditions before operations
   - Use type hints and static analysis
   - Implement defensive programming

2. **Graceful Degradation**
   - Provide fallback functionality
   - Maintain core services during failures
   - Offer alternative solutions
   - Preserve user data during errors

3. **Error Recovery**
   - Implement retry mechanisms with exponential backoff
   - Use circuit breakers for external services
   - Provide clear recovery instructions
   - Log errors for debugging

4. **User Communication**
   - Display user-friendly error messages
   - Provide actionable error information
   - Avoid technical jargon in user-facing messages
   - Offer help and support options

5. **System Resilience**
   - Implement health checks
   - Use timeouts for external calls
   - Design for failure scenarios
   - Monitor system health continuously

## Error Categories

### User Errors:
- Invalid input format
- Insufficient permissions
- Resource not found
- Quota exceeded

### System Errors:
- Network connectivity issues
- Database connection failures
- Memory exhaustion
- Service unavailable

### Logic Errors:
- Invalid state transitions
- Constraint violations
- Business rule violations
- Data inconsistencies

## Implementation Examples

### Error Handling Pattern:
```python
import logging
from typing import Optional, Any
from functools import wraps
import time

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retrying operations with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    delay = base_delay * (2 ** attempt)
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s")
                    time.sleep(delay)
            
            return None
        return wrapper
    return decorator

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: dict) -> dict:
        """Handle errors consistently across the application."""
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'timestamp': time.time()
        }
        
        self.logger.error(f"Error occurred: {error_info}")
        
        # Return user-friendly response
        return {
            'success': False,
            'error': self._get_user_message(error),
            'error_id': id(error),
            'suggestions': self._get_suggestions(error)
        }
    
    def _get_user_message(self, error: Exception) -> str:
        """Convert technical error to user-friendly message."""
        error_messages = {
            'ConnectionError': "Unable to connect to the service. Please check your internet connection.",
            'TimeoutError': "The operation took too long. Please try again.",
            'ValueError': "The provided information is not valid. Please check your input.",
            'PermissionError': "You don't have permission to perform this action."
        }
        return error_messages.get(type(error).__name__, "An unexpected error occurred.")
    
    def _get_suggestions(self, error: Exception) -> list:
        """Provide suggestions for resolving the error."""
        suggestions = {
            'ConnectionError': ["Check internet connection", "Try again later", "Contact support if issue persists"],
            'TimeoutError': ["Try again", "Check if service is available", "Reduce request size"],
            'ValueError': ["Check input format", "Review requirements", "See documentation"]
        }
        return suggestions.get(type(error).__name__, ["Try again", "Contact support"])
```

## Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input format",
    "details": "Email address is not valid",
    "suggestions": [
      "Check email format",
      "Use valid email address"
    ]
  },
  "error_id": "err_123456",
  "timestamp": "2025-11-12T10:30:00Z"
}
```

## Resilience Checklist

- [ ] Input validation implemented
- [ ] Retry mechanisms in place
- [ ] Circuit breakers configured
- [ ] Error logging enabled
- [ ] User-friendly error messages
- [ ] Fallback mechanisms tested
- [ ] Health checks implemented
- [ ] Monitoring and alerting configured