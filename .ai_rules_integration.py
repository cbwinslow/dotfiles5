#!/usr/bin/env python3
"""
 =============================================================================
 AI AGENT RULES INTEGRATION - Universal Agent Compliance System
 =============================================================================
 This Python module provides universal integration for AI agents to automatically
 load and comply with the cbwinslow AI agent rules. It can be imported by any
 AI agent system to ensure compliance.
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

class AIRulesConfig:
    """Configuration for AI Rules integration"""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.rules_file = self.home_dir / ".ai_agent_rules"
        self.rules_loader = self.home_dir / ".ai_rules_loader.sh"
        self.cache_dir = self.home_dir / ".cache" / "ai_rules"
        self.log_file = self.home_dir / "logs" / "ai_rules_enforcement.log"
        
        # Ensure directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.version = "2.0.0"
        self.agent_name = self.detect_agent_type()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def detect_agent_type(self) -> str:
        """Detect the type of AI agent running"""
        # Check environment variables
        env_indicators = {
            'TERM_PROGRAM': {
                'vscode': 'vscode',
                'cursor': 'cursor',
                'hyper': 'hyper'
            },
            'EDITOR': {
                'code': 'vscode',
                'cursor': 'cursor'
            }
        }
        
        for env_var, indicators in env_indicators.items():
            value = os.getenv(env_var, '').lower()
            for indicator, agent_type in indicators.items():
                if indicator in value:
                    return agent_type
        
        # Check running processes
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            processes = result.stdout.lower()
            
            agent_patterns = {
                'opencode': 'opencode',
                'cursor': 'cursor',
                'claude': 'claude',
                'copilot': 'copilot',
                'continue': 'continue',
                'cline': 'cline',
                'aider': 'aider'
            }
            
            for pattern, agent_type in agent_patterns.items():
                if pattern in processes:
                    return agent_type
        except Exception:
            pass
        
        # Check for API keys as indicators
        if os.getenv('OPENAI_API_KEY'):
            return 'openai_agent'
        if os.getenv('ANTHROPIC_API_KEY'):
            return 'anthropic_agent'
        if os.getenv('OPENROUTER_API_KEY'):
            return 'openrouter_agent'
        
        return 'unknown_agent'

# =============================================================================
# RULES LOADER
# =============================================================================

class AIRulesLoader:
    """Main AI Rules loading and enforcement system"""
    
    def __init__(self, config: Optional[AIRulesConfig] = None):
        self.config = config or AIRulesConfig()
        self.logger = self._setup_logging()
        self.rules_loaded = False
        self.rules_data = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the rules system"""
        logger = logging.getLogger('ai_rules')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(self.config.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def load_rules(self) -> bool:
        """Load AI rules from the rules file"""
        try:
            if not self.config.rules_file.exists():
                self.logger.error(f"Rules file not found: {self.config.rules_file}")
                return False
            
            # Source the bash rules file
            result = subprocess.run(
                ['bash', '-c', f'source {self.config.rules_file} && env'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.logger.error(f"Failed to source rules file: {result.stderr}")
                return False
            
            # Parse environment variables from the sourced file
            for line in result.stdout.split('\n'):
                if '=' in line and not line.startswith('_'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    if key.startswith('AI_'):
                        self.rules_data[key] = value
            
            # Set our own variables
            os.environ['AI_RULES_ACTIVE'] = 'true'
            os.environ['AI_RULES_VERSION'] = self.config.version
            os.environ['AI_AGENT_NAME'] = self.config.agent_name
            os.environ['AI_SESSION_ID'] = self.config.session_id
            os.environ['AI_RULES_LOADED_TIME'] = datetime.now().isoformat()
            
            self.rules_loaded = True
            self.logger.info(f"AI rules loaded successfully for {self.config.agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading AI rules: {e}")
            return False
    
    def validate_operation(self, operation: str, target: str = "") -> bool:
        """Validate an operation against AI rules"""
        if not self.rules_loaded:
            if not self.load_rules():
                return False
        
        # Use bash validation functions if available
        try:
            cmd = f'source {self.config.rules_file} && ai_validate_operation "{operation}" "{target}"'
            result = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"Could not validate with bash functions: {e}")
        
        # Fallback validation
        return self._fallback_validation(operation, target)
    
    def _fallback_validation(self, operation: str, target: str) -> bool:
        """Fallback validation when bash functions aren't available"""
        
        # System file protection
        system_dirs = ['/etc/', '/usr/', '/boot/', '/sys/', '/proc/']
        dangerous_ops = ['rm', 'mv', 'chmod', 'chown', 'edit', 'modify']
        
        if operation in dangerous_ops:
            for sys_dir in system_dirs:
                if target.startswith(sys_dir):
                    self.logger.warning(f"Blocked system file operation: {operation} {target}")
                    return False
        
        # SSH protection
        ssh_patterns = ['config', 'known_hosts', 'id_rsa', 'id_ed25519']
        ssh_ops = ['ssh', 'scp', 'sftp']
        
        if operation in ssh_ops:
            for pattern in ssh_patterns:
                if pattern in target:
                    self.logger.warning(f"Blocked SSH operation: {operation} {target}")
                    return False
        
        return True
    
    def log_operation(self, operation: str, target: str = "", result: str = "success"):
        """Log an AI operation for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.config.agent_name,
            'session_id': self.config.session_id,
            'operation': operation,
            'target': target,
            'result': result,
            'compliant': self.validate_operation(operation, target)
        }
        
        # Write to log file
        with open(self.config.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return log_entry

# =============================================================================
# AGENT INTEGRATION DECORATOR
# =============================================================================

def with_ai_rules(agent_name: Optional[str] = None):
    """
    Decorator to automatically apply AI rules to Python functions
    
    Usage:
    @with_ai_rules("my_agent")
    def my_function(file_path):
        # Function will automatically validate operations
        pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Initialize rules loader
            config = AIRulesConfig()
            if agent_name:
                config.agent_name = agent_name
            
            loader = AIRulesLoader(config)
            
            # Load rules if not already loaded
            if not loader.rules_loaded:
                if not loader.load_rules():
                    raise Exception("Failed to load AI rules")
            
            # Log function call
            loader.log_operation(
                operation=f"function_call:{func.__name__}",
                target=str(args)[:100],  # Limit target length
                result="started"
            )
            
            try:
                result = func(*args, **kwargs)
                loader.log_operation(
                    operation=f"function_call:{func.__name__}",
                    target=str(args)[:100],
                    result="success"
                )
                return result
            except Exception as e:
                loader.log_operation(
                    operation=f"function_call:{func.__name__}",
                    target=str(args)[:100],
                    result=f"error:{str(e)}"
                )
                raise
        
        return wrapper
    return decorator

# =============================================================================
# AGENT BASE CLASS
# =============================================================================

class AIAgent:
    """Base class for AI agents with automatic rules compliance"""
    
    def __init__(self, agent_name: Optional[str] = None):
        self.config = AIRulesConfig()
        if agent_name:
            self.config.agent_name = agent_name
        
        self.rules_loader = AIRulesLoader(self.config)
        self.logger = self.rules_loader.logger
        
        # Load rules on initialization
        if not self.rules_loader.load_rules():
            raise Exception("Failed to initialize AI rules")
        
        self.logger.info(f"AI Agent '{self.config.agent_name}' initialized with rules compliance")
    
    def validate_operation(self, operation: str, target: str = "") -> bool:
        """Validate an operation before execution"""
        return self.rules_loader.validate_operation(operation, target)
    
    def safe_file_operation(self, operation: str, file_path: str, **kwargs):
        """Perform file operations with safety checks"""
        if not self.validate_operation(operation, file_path):
            raise Exception(f"Operation '{operation}' on '{file_path}' violates AI rules")
        
        # Log the operation
        self.rules_loader.log_operation(operation, file_path, "attempted")
        
        # Perform the operation (implementation depends on specific operation)
        # This is a placeholder - actual implementation would depend on the operation
        return True
    
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log an AI agent action"""
        details = details or {}
        self.rules_loader.log_operation(
            operation=action,
            target=json.dumps(details)[:200],
            result="logged"
        )

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def initialize_ai_rules(agent_name: Optional[str] = None) -> AIRulesLoader:
    """Initialize AI rules for an agent"""
    config = AIRulesConfig()
    if agent_name:
        config.agent_name = agent_name
    
    loader = AIRulesLoader(config)
    loader.load_rules()
    return loader

def check_compliance() -> Dict[str, Any]:
    """Check current AI rules compliance status"""
    config = AIRulesConfig()
    
    compliance_data = {
        'timestamp': datetime.now().isoformat(),
        'rules_file_exists': config.rules_file.exists(),
        'rules_active': os.getenv('AI_RULES_ACTIVE') == 'true',
        'agent_name': os.getenv('AI_AGENT_NAME', 'unknown'),
        'session_id': os.getenv('AI_SESSION_ID', 'unknown'),
        'rules_version': os.getenv('AI_RULES_VERSION', 'unknown'),
        'loaded_time': os.getenv('AI_RULES_LOADED_TIME', 'unknown')
    }
    
    return compliance_data

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Example usage
    print("🤖 AI Rules Integration System")
    print("=" * 40)
    
    # Check compliance
    compliance = check_compliance()
    print(f"Rules Active: {compliance['rules_active']}")
    print(f"Agent Name: {compliance['agent_name']}")
    print(f"Session ID: {compliance['session_id']}")
    
    # Initialize rules
    loader = initialize_ai_rules()
    if loader.rules_loaded:
        print("✅ AI rules loaded successfully")
        
        # Test validation
        test_ops = [
            ("read", "/home/user/file.txt"),
            ("rm", "/etc/passwd"),
            ("ssh", "config")
        ]
        
        for op, target in test_ops:
            result = loader.validate_operation(op, target)
            print(f"Validation: {op} {target} -> {'✅' if result else '❌'}")
    else:
        print("❌ Failed to load AI rules")