# Memory Management Rules

**Priority:** High
**Applies To:** All AI agents with memory capabilities
**Last Updated:** 2025-11-12
**Updated By:** System

## Rules

1. **Memory Allocation**
   - Always check available memory before allocation
   - Use appropriate data structures for memory efficiency
   - Implement memory pooling for frequent allocations
   - Set reasonable limits on memory usage

2. **Memory Cleanup**
   - Release memory immediately when no longer needed
   - Implement proper garbage collection practices
   - Clear sensitive data from memory after use
   - Use weak references where appropriate

3. **Memory Monitoring**
   - Track memory usage patterns
   - Set up alerts for memory leaks
   - Monitor peak memory consumption
   - Log memory allocation events

4. **Optimization Strategies**
   - Use streaming for large data processing
   - Implement lazy loading where possible
   - Cache frequently accessed data efficiently
   - Compress data stored in memory

## Examples

### Good Example:
```python
class MemoryManager:
    def __init__(self, max_memory_mb: int = 1024):
        self.max_memory = max_memory_mb * 1024 * 1024
        self.current_usage = 0
        self.allocations = {}
    
    def allocate(self, key: str, size: int) -> bool:
        if self.current_usage + size > self.max_memory:
            self.cleanup_old_allocations()
        
        if self.current_usage + size <= self.max_memory:
            self.allocations[key] = size
            self.current_usage += size
            return True
        return False
    
    def deallocate(self, key: str):
        if key in self.allocations:
            self.current_usage -= self.allocations[key]
            del self.allocations[key]
```

## Memory Limits by Agent Type

- **Chat Agents:** 512MB maximum
- **Code Generation:** 1GB maximum  
- **Data Processing:** 2GB maximum
- **Analysis Agents:** 768MB maximum