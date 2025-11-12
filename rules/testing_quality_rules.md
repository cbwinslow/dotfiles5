# Testing and Quality Assurance Rules

**Priority:** High
**Applies To:** All AI agents
**Last Updated:** 2025-11-12
**Updated By:** System

## Rules

1. **Test Coverage**
   - Maintain minimum 80% code coverage
   - Test all critical paths and edge cases
   - Include integration tests for workflows
   - Test error conditions and exceptions

2. **Test Types**
   - Unit tests for individual functions
   - Integration tests for component interactions
   - End-to-end tests for complete workflows
   - Performance tests for critical operations

3. **Test Quality**
   - Write clear, descriptive test names
   - Use arrange-act-assert pattern
   - Test one thing per test case
   - Maintain test independence

4. **Automated Testing**
   - Integrate tests into CI/CD pipeline
   - Run tests on every commit
   - Use test data factories
   - Implement test parallelization

5. **Quality Gates**
   - All tests must pass before deployment
   - Code coverage requirements met
   - Performance benchmarks satisfied
   - Security scans completed

## Testing Framework Examples

### Unit Testing:
```python
import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

class TestDataProcessor:
    def setup_method(self):
        """Setup test environment."""
        self.processor = DataProcessor()
        self.sample_data = [{"id": 1, "value": 100}]
    
    def test_process_valid_data(self):
        """Test processing of valid data."""
        # Arrange
        expected_result = {"processed": 1, "total": 100}
        
        # Act
        result = self.processor.process(self.sample_data)
        
        # Assert
        assert result == expected_result
        assert result["processed"] == 1
    
    def test_process_empty_data(self):
        """Test processing of empty data."""
        # Arrange
        empty_data = []
        
        # Act & Assert
        with pytest.raises(ValueError, match="Data cannot be empty"):
            self.processor.process(empty_data)
    
    @patch('external_api.call_service')
    def test_external_service_integration(self, mock_service):
        """Test integration with external service."""
        # Arrange
        mock_service.return_value = {"status": "success"}
        
        # Act
        result = self.processor.call_external_service()
        
        # Assert
        assert result["status"] == "success"
        mock_service.assert_called_once()
```

### Integration Testing:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestAPIIntegration:
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_complete_workflow(self):
        """Test complete API workflow."""
        # Create resource
        response = self.client.post("/api/resources", json={"name": "test"})
        assert response.status_code == 201
        resource_id = response.json()["id"]
        
        # Get resource
        response = self.client.get(f"/api/resources/{resource_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "test"
        
        # Update resource
        response = self.client.put(f"/api/resources/{resource_id}", 
                                 json={"name": "updated"})
        assert response.status_code == 200
        
        # Delete resource
        response = self.client.delete(f"/api/resources/{resource_id}")
        assert response.status_code == 204
```

## Test Data Management

### Test Factories:
```python
import factory
from factory import fuzzy
from datetime import datetime, timedelta

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker('name')
    email = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '.')}@example.com")
    created_at = factory.LazyFunction(datetime.now)
    is_active = True

class TestDataFactory:
    @staticmethod
    def create_test_users(count: int = 5) -> List[User]:
        """Create test users for testing."""
        return [UserFactory() for _ in range(count)]
    
    @staticmethod
    def create_test_data_with_relationships() -> Dict[str, Any]:
        """Create complex test data with relationships."""
        user = UserFactory()
        posts = [PostFactory(user=user) for _ in range(3)]
        return {"user": user, "posts": posts}
```

## Performance Testing

### Load Testing:
```python
import time
import concurrent.futures
from typing import List

def performance_test_concurrent_requests(url: str, num_requests: int = 100) -> Dict[str, float]:
    """Test performance under concurrent load."""
    start_time = time.time()
    
    def make_request():
        response = requests.get(url)
        return response.status_code == 200
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        results = [f.result() for f in futures]
    
    end_time = time.time()
    
    return {
        "total_time": end_time - start_time,
        "success_rate": sum(results) / len(results),
        "requests_per_second": num_requests / (end_time - start_time)
    }
```

## Quality Metrics

### Code Quality Indicators:
- **Coverage:** ≥ 80%
- **Complexity:** ≤ 10 per function
- **Duplication:** ≤ 3%
- **Maintainability Index:** ≥ 70

### Performance Benchmarks:
- **Response Time:** ≤ 2s (95th percentile)
- **Throughput:** ≥ 100 requests/second
- **Error Rate:** ≤ 1%
- **Availability:** ≥ 99.9%

## Testing Checklist

- [ ] Unit tests written for all functions
- [ ] Integration tests cover workflows
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] Performance tests implemented
- [ ] Security tests included
- [ ] Test data properly managed
- [ ] CI/CD integration complete
- [ ] Coverage requirements met
- [ ] Quality gates configured