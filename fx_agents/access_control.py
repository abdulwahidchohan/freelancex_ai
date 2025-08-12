#!/usr/bin/env python3
"""
Enhanced Access Control System for FreelanceX.AI
Provides comprehensive access management and permissions
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class PermissionLevel(Enum):
    """Permission levels for system access"""
    READ_ONLY = "read_only"
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ADMIN = "admin"
    FULL_ACCESS = "full_access"

class ResourceType(Enum):
    """Types of resources that can be accessed"""
    AGENT = "agent"
    TOOL = "tool"
    API = "api"
    DATABASE = "database"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    MEMORY = "memory"
    TRACING = "tracing"

class AccessRequest(BaseModel):
    """Access request model"""
    user_id: str = Field(..., description="User identifier")
    resource_type: ResourceType = Field(..., description="Type of resource being accessed")
    resource_name: str = Field(..., description="Name of the specific resource")
    permission_level: PermissionLevel = Field(..., description="Requested permission level")
    context: Dict[str, Any] = Field(default_factory=dict, description="Request context")
    timestamp: datetime = Field(default_factory=datetime.now, description="Request timestamp")

class AccessGrant(BaseModel):
    """Access grant model"""
    user_id: str = Field(..., description="User identifier")
    resource_type: ResourceType = Field(..., description="Type of resource")
    resource_name: str = Field(..., description="Name of the resource")
    permission_level: PermissionLevel = Field(..., description="Granted permission level")
    granted_at: datetime = Field(default_factory=datetime.now, description="Grant timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Access conditions")

class SystemPermissions(BaseModel):
    """System-wide permissions configuration"""
    default_level: PermissionLevel = Field(default=PermissionLevel.STANDARD, description="Default permission level")
    admin_users: List[str] = Field(default_factory=list, description="Admin user IDs")
    restricted_resources: List[str] = Field(default_factory=list, description="Restricted resource names")
    api_key_required: bool = Field(default=True, description="Whether API key is required")
    session_validation: bool = Field(default=True, description="Whether session validation is required")
    rate_limiting: bool = Field(default=True, description="Whether rate limiting is enabled")

class AccessControlManager:
    """Enhanced access control manager"""
    
    def __init__(self, config: Optional[SystemPermissions] = None):
        self.config = config or SystemPermissions()
        self.access_grants: Dict[str, AccessGrant] = {}
        self.access_log: List[AccessRequest] = []
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Initialize default permissions
        self._initialize_default_permissions()
    
    def _initialize_default_permissions(self):
        """Initialize default system permissions"""
        # Grant full access to admin users
        for admin_user in self.config.admin_users:
            self.grant_access(
                user_id=admin_user,
                resource_type=ResourceType.SYSTEM,
                resource_name="*",
                permission_level=PermissionLevel.FULL_ACCESS
            )
        
        logger.info(f"Initialized access control with {len(self.config.admin_users)} admin users")
    
    def request_access(self, request: AccessRequest) -> bool:
        """Request access to a resource"""
        try:
            # Log the access request
            self.access_log.append(request)
            
            # Check if user is admin
            if request.user_id in self.config.admin_users:
                logger.info(f"Admin access granted to {request.user_id} for {request.resource_name}")
                return True
            
            # Check existing grants
            grant_key = f"{request.user_id}:{request.resource_type.value}:{request.resource_name}"
            if grant_key in self.access_grants:
                grant = self.access_grants[grant_key]
                if not grant.expires_at or grant.expires_at > datetime.now():
                    if self._has_sufficient_permission(grant.permission_level, request.permission_level):
                        logger.info(f"Access granted to {request.user_id} for {request.resource_name}")
                        return True
            
            # Check default permissions
            if self._has_sufficient_permission(self.config.default_level, request.permission_level):
                if request.resource_name not in self.config.restricted_resources:
                    logger.info(f"Default access granted to {request.user_id} for {request.resource_name}")
                    return True
            
            logger.warning(f"Access denied to {request.user_id} for {request.resource_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error processing access request: {str(e)}")
            return False
    
    def grant_access(self, user_id: str, resource_type: ResourceType, resource_name: str,
                    permission_level: PermissionLevel, expires_in_hours: Optional[int] = None,
                    conditions: Optional[Dict[str, Any]] = None) -> bool:
        """Grant access to a resource"""
        try:
            grant = AccessGrant(
                user_id=user_id,
                resource_type=resource_type,
                resource_name=resource_name,
                permission_level=permission_level,
                expires_at=datetime.now() + timedelta(hours=expires_in_hours) if expires_in_hours else None,
                conditions=conditions or {}
            )
            
            grant_key = f"{user_id}:{resource_type.value}:{resource_name}"
            self.access_grants[grant_key] = grant
            
            logger.info(f"Access granted to {user_id} for {resource_name} with {permission_level.value} permissions")
            return True
            
        except Exception as e:
            logger.error(f"Error granting access: {str(e)}")
            return False
    
    def revoke_access(self, user_id: str, resource_type: ResourceType, resource_name: str) -> bool:
        """Revoke access to a resource"""
        try:
            grant_key = f"{user_id}:{resource_type.value}:{resource_name}"
            if grant_key in self.access_grants:
                del self.access_grants[grant_key]
                logger.info(f"Access revoked from {user_id} for {resource_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error revoking access: {str(e)}")
            return False
    
    def check_rate_limit(self, user_id: str, max_requests: int = 100, window_minutes: int = 60) -> bool:
        """Check if user has exceeded rate limits"""
        try:
            if not self.config.rate_limiting:
                return True
            
            now = datetime.now()
            window_start = now - timedelta(minutes=window_minutes)
            
            # Get user's request history
            user_requests = self.rate_limits.get(user_id, [])
            
            # Remove old requests outside the window
            user_requests = [req for req in user_requests if req > window_start]
            
            # Check if limit exceeded
            if len(user_requests) >= max_requests:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return False
            
            # Add current request
            user_requests.append(now)
            self.rate_limits[user_id] = user_requests
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return True  # Allow access on error
    
    def _has_sufficient_permission(self, granted: PermissionLevel, required: PermissionLevel) -> bool:
        """Check if granted permission is sufficient for required permission"""
        permission_hierarchy = {
            PermissionLevel.READ_ONLY: 1,
            PermissionLevel.BASIC: 2,
            PermissionLevel.STANDARD: 3,
            PermissionLevel.ADVANCED: 4,
            PermissionLevel.ADMIN: 5,
            PermissionLevel.FULL_ACCESS: 6
        }
        
        return permission_hierarchy.get(granted, 0) >= permission_hierarchy.get(required, 0)
    
    def get_user_permissions(self, user_id: str) -> List[AccessGrant]:
        """Get all permissions for a user"""
        try:
            user_grants = []
            for grant in self.access_grants.values():
                if grant.user_id == user_id and (not grant.expires_at or grant.expires_at > datetime.now()):
                    user_grants.append(grant)
            return user_grants
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}")
            return []
    
    def cleanup_expired_grants(self):
        """Remove expired access grants"""
        try:
            now = datetime.now()
            expired_keys = []
            
            for key, grant in self.access_grants.items():
                if grant.expires_at and grant.expires_at <= now:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.access_grants[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired access grants")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired grants: {str(e)}")

# Global access control manager
_access_control_manager: Optional[AccessControlManager] = None

def get_access_control_manager() -> AccessControlManager:
    """Get the global access control manager"""
    global _access_control_manager
    if _access_control_manager is None:
        config = SystemPermissions(
            admin_users=os.getenv("FREELANCEX_ADMIN_USERS", "").split(",") if os.getenv("FREELANCEX_ADMIN_USERS") else [],
            api_key_required=os.getenv("FREELANCEX_API_KEY_REQUIRED", "true").lower() == "true",
            session_validation=os.getenv("FREELANCEX_SESSION_VALIDATION", "true").lower() == "true",
            rate_limiting=os.getenv("FREELANCEX_RATE_LIMITING", "true").lower() == "true"
        )
        _access_control_manager = AccessControlManager(config)
    return _access_control_manager

def require_access(resource_type: ResourceType, resource_name: str, permission_level: PermissionLevel = PermissionLevel.STANDARD):
    """Decorator to require access for function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract user_id from args or kwargs
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            
            if not user_id:
                logger.error("No user_id provided for access control")
                return None
            
            # Check access
            manager = get_access_control_manager()
            request = AccessRequest(
                user_id=user_id,
                resource_type=resource_type,
                resource_name=resource_name,
                permission_level=permission_level
            )
            
            if not manager.request_access(request):
                logger.error(f"Access denied for {user_id} to {resource_name}")
                return None
            
            # Check rate limit
            if not manager.check_rate_limit(user_id):
                logger.error(f"Rate limit exceeded for {user_id}")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Initialize access control on module import
get_access_control_manager()
