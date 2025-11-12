# Security and Privacy Rules

**Priority:** Critical
**Applies To:** All AI agents
**Last Updated:** 2025-11-12
**Updated By:** System

## Rules

1. **Data Protection**
   - Never store or transmit sensitive personal information
   - Encrypt all data at rest and in transit
   - Implement data minimization principles
   - Use anonymization techniques for user data

2. **Access Control**
   - Implement proper authentication mechanisms
   - Use principle of least privilege
   - Log all access attempts
   - Regular audit of permissions

3. **Input Validation**
   - Validate all user inputs before processing
   - Sanitize data to prevent injection attacks
   - Implement rate limiting for API endpoints
   - Use allowlists rather than blocklists

4. **Secure Communication**
   - Use HTTPS for all network communications
   - Implement certificate pinning where appropriate
   - Use secure protocols for data exchange
   - Verify message integrity

5. **Vulnerability Management**
   - Keep all dependencies updated
   - Regular security scans and assessments
   - Prompt patching of identified vulnerabilities
   - Monitor security advisories

## Prohibited Actions

- Never expose API keys or credentials
- Never log sensitive user data
- Never bypass security controls
- Never use insecure cryptographic practices

## Examples

### Secure Input Validation:
```python
import re
from typing import Optional

def validate_user_input(input_string: str, max_length: int = 1000) -> Optional[str]:
    """
    Validate and sanitize user input.
    
    Args:
        input_string: Raw user input
        max_length: Maximum allowed length
        
    Returns:
        Sanitized input or None if invalid
    """
    if not input_string or len(input_string) > max_length:
        return None
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_string.strip())
    
    # Additional validation based on context
    if not sanitized or len(sanitized) == 0:
        return None
        
    return sanitized
```

## Security Checklist

- [ ] All inputs validated
- [ ] Sensitive data encrypted
- [ ] Access controls implemented
- [ ] Logging enabled
- [ ] Dependencies updated
- [ ] Security review completed