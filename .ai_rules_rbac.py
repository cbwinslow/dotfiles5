#!/usr/bin/env python3
"""
 =============================================================================
 AI RULES ROLE-BASED ACCESS CONTROL (RBAC) SYSTEM
 =============================================================================
 Enterprise-grade role-based access control for AI Rules system.
 Provides granular permissions, role management, and access auditing.
"""

import os
import sys
import json
import hashlib
import jwt
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import logging

# Add home directory to path
sys.path.append(str(Path.home()))

# =============================================================================
# CONFIGURATION
# =============================================================================

class Permission(Enum):
    """System permissions"""
    READ_RULES = "read_rules"
    WRITE_RULES = "write_rules"
    DELETE_RULES = "delete_rules"
    EXECUTE_RULES = "execute_rules"
    MODIFY_CONFIG = "modify_config"
    VIEW_LOGS = "view_logs"
    MANAGE_BACKUPS = "manage_backups"
    DEPLOY_SYSTEM = "deploy_system"
    MONITOR_SYSTEM = "monitor_system"
    MANAGE_USERS = "manage_users"
    SYSTEM_ADMIN = "system_admin"

class Role(Enum):
    """System roles"""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMINISTRATOR = "administrator"
    SYSTEM_ADMIN = "system_admin"
    AI_AGENT = "ai_agent"
    SECURITY_AUDITOR = "security_auditor"

@dataclass
class User:
    """User entity"""
    username: str
    email: str
    roles: List[Role]
    created_at: datetime
    last_login: Optional[datetime] = None
    active: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AccessPolicy:
    """Access policy definition"""
    name: str
    description: str
    permissions: List[Permission]
    resource_patterns: List[str]
    conditions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}

@dataclass
class AccessSession:
    """Access session for user"""
    session_id: str
    username: str
    roles: List[Role]
    permissions: Set[Permission]
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid"""
        return not self.is_expired() and self.last_activity > (datetime.now() - timedelta(hours=1))

# =============================================================================
# RBAC CORE SYSTEM
# =============================================================================

class AIRulesRBAC:
    """Role-Based Access Control system for AI Rules"""
    
    def __init__(self, db_path: Optional[str] = None, secret_key: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / ".cache" / "ai_rules_rbac.db")
        
        if secret_key is None:
            secret_key = os.environ.get('AI_RULES_RBAC_SECRET', 'default-secret-change-me')
        
        self.db_path = db_path
        self.secret_key = secret_key
        self.logger = self._setup_logging()
        
        # Initialize database
        self._init_database()
        
        # Initialize default roles and policies
        self._init_default_roles()
        self._init_default_policies()
        
        # Session management
        self._active_sessions: Dict[str, AccessSession] = {}
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for RBAC system"""
        logger = logging.getLogger('ai_rules_rbac')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler
        log_file = Path.home() / "logs" / "ai_rules_rbac.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _init_database(self):
        """Initialize SQLite database for RBAC"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Users table
        self._conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                password_hash TEXT,
                roles TEXT,  -- JSON array
                created_at TIMESTAMP,
                last_login TIMESTAMP,
                active BOOLEAN DEFAULT 1,
                metadata TEXT  -- JSON object
            )
        ''')
        
        # Roles table
        self._conn.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                role_name TEXT PRIMARY KEY,
                permissions TEXT,  -- JSON array
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Policies table
        self._conn.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                policy_name TEXT PRIMARY KEY,
                description TEXT,
                permissions TEXT,  -- JSON array
                resource_patterns TEXT,  -- JSON array
                conditions TEXT,  -- JSON object
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Access logs table
        self._conn.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                session_id TEXT,
                action TEXT,
                resource TEXT,
                permission TEXT,
                granted BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT  -- JSON object
            )
        ''')
        
        # Sessions table
        self._conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT,
                roles TEXT,  -- JSON array
                permissions TEXT,  -- JSON array
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                last_activity TIMESTAMP,
                metadata TEXT  -- JSON object
            )
        ''')
        
        self._conn.commit()
    
    def _init_default_roles(self):
        """Initialize default system roles"""
        default_roles = {
            Role.VIEWER.value: [
                Permission.READ_RULES,
                Permission.VIEW_LOGS
            ],
            Role.OPERATOR.value: [
                Permission.READ_RULES,
                Permission.EXECUTE_RULES,
                Permission.VIEW_LOGS,
                Permission.MONITOR_SYSTEM
            ],
            Role.ADMINISTRATOR.value: [
                Permission.READ_RULES,
                Permission.WRITE_RULES,
                Permission.EXECUTE_RULES,
                Permission.MODIFY_CONFIG,
                Permission.VIEW_LOGS,
                Permission.MANAGE_BACKUPS,
                Permission.DEPLOY_SYSTEM,
                Permission.MONITOR_SYSTEM
            ],
            Role.SYSTEM_ADMIN.value: list(Permission),  # All permissions
            Role.AI_AGENT.value: [
                Permission.READ_RULES,
                Permission.EXECUTE_RULES
            ],
            Role.SECURITY_AUDITOR.value: [
                Permission.READ_RULES,
                Permission.VIEW_LOGS,
                Permission.MONITOR_SYSTEM
            ]
        }
        
        for role_name, permissions in default_roles.items():
            self._conn.execute('''
                INSERT OR REPLACE INTO roles (role_name, permissions, description)
                VALUES (?, ?, ?)
            ''', (
                role_name,
                json.dumps([p.value for p in permissions]),
                f"Default role: {role_name}"
            ))
        
        self._conn.commit()
    
    def _init_default_policies(self):
        """Initialize default access policies"""
        default_policies = [
            AccessPolicy(
                name="ai_agent_basic_access",
                description="Basic access for AI agents",
                permissions=[Permission.READ_RULES, Permission.EXECUTE_RULES],
                resource_patterns=["ai_rules:*", "validation:*"],
                conditions={"agent_type": "*", "session_timeout": 3600}
            ),
            AccessPolicy(
                name="admin_full_access",
                description="Full access for administrators",
                permissions=list(Permission),
                resource_patterns=["*"],
                conditions={"require_mfa": True}
            ),
            AccessPolicy(
                name="viewer_readonly",
                description="Read-only access for viewers",
                permissions=[Permission.READ_RULES, Permission.VIEW_LOGS],
                resource_patterns=["rules:*", "logs:*"],
                conditions={"read_only": True}
            )
        ]
        
        for policy in default_policies:
            self._conn.execute('''
                INSERT OR REPLACE INTO policies (policy_name, description, permissions, resource_patterns, conditions)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                policy.name,
                policy.description,
                json.dumps([p.value for p in policy.permissions]),
                json.dumps(policy.resource_patterns),
                json.dumps(policy.conditions)
            ))
        
        self._conn.commit()
    
    # =============================================================================
    # USER MANAGEMENT
    # =============================================================================
    
    def create_user(self, username: str, email: str, password: str, roles: List[Role]) -> bool:
        """Create a new user"""
        try:
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Check if user exists
            cursor = self._conn.cursor()
            cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                self.logger.warning(f"User already exists: {username}")
                return False
            
            # Create user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, roles, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                username,
                email,
                password_hash,
                json.dumps([r.value for r in roles]),
                datetime.now().isoformat()
            ))
            
            self._conn.commit()
            self.logger.info(f"User created: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating user {username}: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and create session"""
        try:
            cursor = self._conn.cursor()
            cursor.execute('''
                SELECT username, roles, active FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, hashlib.sha256(password.encode()).hexdigest()))
            
            row = cursor.fetchone()
            if not row:
                self.logger.warning(f"Authentication failed for: {username}")
                return None
            
            if not row[2]:  # active flag
                self.logger.warning(f"Inactive user attempted login: {username}")
                return None
            
            # Get user permissions
            roles = [Role(r) for r in json.loads(row[1])]
            permissions = self._get_role_permissions(roles)
            
            # Create session
            session_id = self._create_session(username, roles, permissions)
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE username = ?
            ''', (datetime.now().isoformat(), username))
            self._conn.commit()
            
            self.logger.info(f"User authenticated: {username}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error authenticating user {username}: {e}")
            return None
    
    def _create_session(self, username: str, roles: List[Role], permissions: Set[Permission]) -> str:
        """Create access session"""
        session_id = hashlib.sha256(f"{username}{time.time()}{self.secret_key}".encode()).hexdigest()
        expires_at = datetime.now() + timedelta(hours=8)  # 8 hour sessions
        
        session = AccessSession(
            session_id=session_id,
            username=username,
            roles=roles,
            permissions=permissions,
            created_at=datetime.now(),
            expires_at=expires_at,
            last_activity=datetime.now()
        )
        
        # Store in memory
        self._active_sessions[session_id] = session
        
        # Store in database
        self._conn.execute('''
            INSERT OR REPLACE INTO sessions 
            (session_id, username, roles, permissions, created_at, expires_at, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            username,
            json.dumps([r.value for r in roles]),
            json.dumps([p.value for p in permissions]),
            session.created_at.isoformat(),
            session.expires_at.isoformat(),
            session.last_activity.isoformat()
        ))
        
        self._conn.commit()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[AccessSession]:
        """Validate session and return session data"""
        # Check memory cache first
        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            if session.is_valid():
                session.last_activity = datetime.now()
                return session
            else:
                # Remove expired session
                del self._active_sessions[session_id]
                self._cleanup_session(session_id)
                return None
        
        # Check database
        cursor = self._conn.cursor()
        cursor.execute('''
            SELECT username, roles, permissions, created_at, expires_at, last_activity
            FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        session = AccessSession(
            session_id=session_id,
            username=row[0],
            roles=[Role(r) for r in json.loads(row[1])],
            permissions=set(Permission(p) for p in json.loads(row[2])),
            created_at=datetime.fromisoformat(row[3]),
            expires_at=datetime.fromisoformat(row[4]),
            last_activity=datetime.fromisoformat(row[5])
        )
        
        if session.is_valid():
            # Add to memory cache
            self._active_sessions[session_id] = session
            session.last_activity = datetime.now()
            return session
        else:
            # Clean up expired session
            self._cleanup_session(session_id)
            return None
    
    def _cleanup_session(self, session_id: str):
        """Clean up expired session"""
        self._conn.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        self._conn.commit()
    
    def _get_role_permissions(self, roles: List[Role]) -> Set[Permission]:
        """Get permissions for roles"""
        permissions = set()
        
        for role in roles:
            cursor = self._conn.cursor()
            cursor.execute('SELECT permissions FROM roles WHERE role_name = ?', (role.value,))
            row = cursor.fetchone()
            if row:
                role_permissions = json.loads(row[0])
                permissions.update(Permission(p) for p in role_permissions)
        
        return permissions
    
    # =============================================================================
    # ACCESS CONTROL
    # =============================================================================
    
    def check_permission(self, session_id: str, permission: Permission, resource: str = "*") -> bool:
        """Check if session has permission for resource"""
        session = self.validate_session(session_id)
        if not session:
            self.logger.warning(f"Invalid session for permission check: {session_id}")
            return False
        
        # Check direct permission
        has_permission = permission in session.permissions
        
        # Log access attempt
        self._log_access(
            username=session.username,
            session_id=session_id,
            action="check_permission",
            resource=resource,
            permission=permission.value,
            granted=has_permission
        )
        
        return has_permission
    
    def require_permission(self, session_id: str, permission: Permission, resource: str = "*"):
        """Decorator to require permission for function execution"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.check_permission(session_id, permission, resource):
                    raise PermissionError(f"Permission denied: {permission.value} on {resource}")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def _log_access(self, username: str, session_id: str, action: str, 
                   resource: str, permission: str, granted: bool, details: Dict[str, Any] = None):
        """Log access attempt"""
        try:
            cursor = self._conn.cursor()
            cursor.execute('''
                INSERT INTO access_logs 
                (username, session_id, action, resource, permission, granted, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                username,
                session_id,
                action,
                resource,
                permission,
                granted,
                json.dumps(details or {})
            ))
            self._conn.commit()
        except Exception as e:
            self.logger.error(f"Error logging access: {e}")
    
    # =============================================================================
    # POLICY MANAGEMENT
    # =============================================================================
    
    def evaluate_policy(self, session_id: str, policy_name: str, context: Dict[str, Any]) -> bool:
        """Evaluate access policy against context"""
        session = self.validate_session(session_id)
        if not session:
            return False
        
        cursor = self._conn.cursor()
        cursor.execute('''
            SELECT permissions, resource_patterns, conditions FROM policies WHERE policy_name = ?
        ''', (policy_name,))
        
        row = cursor.fetchone()
        if not row:
            return False
        
        permissions = json.loads(row[0])
        resource_patterns = json.loads(row[1])
        conditions = json.loads(row[2])
        
        # Check permissions
        session_permissions = [p.value for p in session.permissions]
        if not any(p in session_permissions for p in permissions):
            return False
        
        # Check resource patterns
        resource = context.get('resource', '')
        if not any(pattern.replace('*', '') in resource for pattern in resource_patterns):
            return False
        
        # Check conditions
        for condition_key, condition_value in conditions.items():
            if condition_key not in context:
                return False
            
            if isinstance(condition_value, str) and condition_value == '*':
                continue  # Wildcard, always matches
            
            if context[condition_key] != condition_value:
                return False
        
        return True
    
    # =============================================================================
    # AUDITING AND REPORTING
    # =============================================================================
    
    def get_access_logs(self, username: Optional[str] = None, 
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Get access logs with filtering"""
        cursor = self._conn.cursor()
        query = 'SELECT * FROM access_logs WHERE 1=1'
        params = []
        
        if username:
            query += ' AND username = ?'
            params.append(username)
        
        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time.isoformat())
        
        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time.isoformat())
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to dictionaries
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_user_summary(self, username: str) -> Dict[str, Any]:
        """Get user access summary"""
        cursor = self._conn.cursor()
        
        # User info
        cursor.execute('''
            SELECT username, email, roles, created_at, last_login, active
            FROM users WHERE username = ?
        ''', (username,))
        
        user_row = cursor.fetchone()
        if not user_row:
            return {}
        
        # Recent access logs
        cursor.execute('''
            SELECT action, resource, permission, granted, timestamp
            FROM access_logs 
            WHERE username = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (username,))
        
        access_logs = []
        for row in cursor.fetchall():
            access_logs.append({
                'action': row[0],
                'resource': row[1],
                'permission': row[2],
                'granted': row[3],
                'timestamp': row[4]
            })
        
        return {
            'username': user_row[0],
            'email': user_row[1],
            'roles': json.loads(user_row[2]),
            'created_at': user_row[3],
            'last_login': user_row[4],
            'active': bool(user_row[5]),
            'recent_access': access_logs
        }
    
    def generate_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        # Get access statistics
        cursor = self._conn.cursor()
        cursor.execute('''
            SELECT username, COUNT(*) as access_count, 
                   SUM(CASE WHEN granted = 1 THEN 1 ELSE 0 END) as granted_count,
                   SUM(CASE WHEN granted = 0 THEN 1 ELSE 0 END) as denied_count
            FROM access_logs 
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY username
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        user_stats = []
        for row in cursor.fetchall():
            user_stats.append({
                'username': row[0],
                'total_access': row[1],
                'granted': row[2],
                'denied': row[3],
                'success_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0
            })
        
        # Get permission usage
        cursor.execute('''
            SELECT permission, COUNT(*) as usage_count
            FROM access_logs 
            WHERE timestamp BETWEEN ? AND ? AND granted = 1
            GROUP BY permission
            ORDER BY usage_count DESC
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        permission_usage = []
        for row in cursor.fetchall():
            permission_usage.append({
                'permission': row[0],
                'usage_count': row[1]
            })
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'user_statistics': user_stats,
            'permission_usage': permission_usage,
            'generated_at': datetime.now().isoformat()
        }

# =============================================================================
# INTEGRATION WITH AI RULES
# =============================================================================

class RBACProtectedAIRules:
    """AI Rules system with RBAC protection"""
    
    def __init__(self, rbac: AIRulesRBAC):
        self.rbac = rbac
        self.logger = logging.getLogger('rbac_protected_ai_rules')
    
    def validate_operation_with_rbac(self, session_id: str, operation: str, target: str) -> bool:
        """Validate operation with RBAC check"""
        # Check RBAC permission first
        if not self.rbac.check_permission(session_id, Permission.EXECUTE_RULES, f"operation:{operation}"):
            self.logger.warning(f"RBAC denied operation: {operation} on {target}")
            return False
        
        # Then perform normal validation
        try:
            from ai_rules_integration import AIRulesLoader
            loader = AIRulesLoader()
            result = loader.validate_operation(operation, target)
            
            # Log the operation
            self.rbac._log_access(
                username=self.rbac.validate_session(session_id).username,
                session_id=session_id,
                action="validate_operation",
                resource=target,
                permission=Permission.EXECUTE_RULES.value,
                granted=result,
                details={'operation': operation}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in operation validation: {e}")
            return False
    
    def modify_rules_with_rbac(self, session_id: str, modification: Dict[str, Any]) -> bool:
        """Modify AI rules with RBAC check"""
        # Check RBAC permission
        if not self.rbac.check_permission(session_id, Permission.WRITE_RULES, "rules:modify"):
            self.logger.warning(f"RBAC denied rules modification")
            return False
        
        # Perform modification (implementation depends on specific modification type)
        self.logger.info(f"Rules modification approved for session: {session_id}")
        return True

# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for RBAC system"""
    import argparse
    import getpass
    
    parser = argparse.ArgumentParser(description='AI Rules RBAC System')
    parser.add_argument('command', choices=[
        'create-user', 'login', 'check-permission', 'audit-report', 
        'user-summary', 'list-users', 'create-session'
    ], help='Command to execute')
    parser.add_argument('--username', help='Username')
    parser.add_argument('--email', help='Email address')
    parser.add_argument('--session', help='Session ID')
    parser.add_argument('--permission', help='Permission to check')
    parser.add_argument('--resource', help='Resource for permission check')
    parser.add_argument('--days', type=int, default=7, help='Days for audit report')
    
    args = parser.parse_args()
    
    # Initialize RBAC
    rbac = AIRulesRBAC()
    
    if args.command == 'create-user':
        if not args.username or not args.email:
            print("Username and email required")
            return
        
        password = getpass.getpass("Password: ")
        roles = [Role.VIEWER]  # Default role
        
        if rbac.create_user(args.username, args.email, password, roles):
            print(f"User {args.username} created successfully")
        else:
            print("Failed to create user")
    
    elif args.command == 'login':
        if not args.username:
            print("Username required")
            return
        
        password = getpass.getpass("Password: ")
        session_id = rbac.authenticate_user(args.username, password)
        
        if session_id:
            print(f"Login successful. Session ID: {session_id}")
        else:
            print("Login failed")
    
    elif args.command == 'check-permission':
        if not args.session or not args.permission:
            print("Session ID and permission required")
            return
        
        try:
            permission = Permission(args.permission)
            resource = args.resource or "*"
            granted = rbac.check_permission(args.session, permission, resource)
            print(f"Permission {args.permission} on {resource}: {'GRANTED' if granted else 'DENIED'}")
        except ValueError:
            print(f"Invalid permission: {args.permission}")
    
    elif args.command == 'audit-report':
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
        
        report = rbac.generate_audit_report(start_date, end_date)
        print(json.dumps(report, indent=2))
    
    elif args.command == 'user-summary':
        if not args.username:
            print("Username required")
            return
        
        summary = rbac.get_user_summary(args.username)
        print(json.dumps(summary, indent=2))
    
    elif args.command == 'list-users':
        cursor = rbac._conn.cursor()
        cursor.execute('SELECT username, email, active, last_login FROM users')
        users = cursor.fetchall()
        
        print("Users:")
        for username, email, active, last_login in users:
            status = "Active" if active else "Inactive"
            print(f"  {username} ({email}) - {status} - Last login: {last_login or 'Never'}")

if __name__ == "__main__":
    main()