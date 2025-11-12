# Performance and Optimization Rules

**Priority:** Medium
**Applies To:** All AI agents
**Last Updated:** 2025-11-12
**Updated By:** System

## Rules

1. **Response Time**
   - Aim for sub-2 second response times
   - Implement async operations for long tasks
   - Use caching for frequently requested data
   - Optimize critical code paths

2. **Resource Usage**
   - Monitor CPU and memory usage
   - Implement efficient algorithms
   - Use appropriate data structures
   - Avoid unnecessary computations

3. **Scalability**
   - Design for horizontal scaling
   - Implement load balancing where needed
   - Use connection pooling
   - Optimize database queries

4. **Caching Strategy**
   - Cache expensive computations
   - Use appropriate cache expiration
   - Implement cache invalidation
   - Monitor cache hit rates

5. **Monitoring and Metrics**
   - Track performance metrics
   - Set up alerts for degradation
   - Profile code regularly
   - Monitor user experience metrics

## Optimization Techniques

### Code Optimization:
```python
import functools
import time
from typing import Dict, Any

# Use memoization for expensive functions
@functools.lru_cache(maxsize=128)
def expensive_computation(data: str) -> Dict[str, Any]:
    """Cache results of expensive computations."""
    # Complex computation here
    return result

# Use generators for large datasets
def process_large_dataset(data_source):
    """Process data efficiently using generators."""
    for item in data_source:
        yield process_item(item)

# Implement connection pooling
class ConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.pool = [create_connection() for _ in range(max_connections)]
        self.available = list(range(max_connections))
    
    def get_connection(self):
        if self.available:
            return self.pool[self.available.pop()]
        return None
```

## Performance Benchmarks

### Response Time Targets:
- **Simple queries:** < 500ms
- **Complex analysis:** < 5s
- **Code generation:** < 3s
- **Data processing:** < 10s

### Resource Limits:
- **Memory usage:** < 1GB per request
- **CPU time:** < 30s per request
- **Network calls:** < 10 per request
- **File operations:** < 100MB per request

## Monitoring Checklist

- [ ] Response time monitoring
- [ ] Resource usage tracking
- [ ] Error rate monitoring
- [ ] Cache performance metrics
- [ ] User experience scores
- [ ] Regular performance reviews