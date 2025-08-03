#!/usr/bin/env python3
"""
FreelanceX.AI API Gateway
Centralized request management, routing, rate limiting, and security layer
"""

import asyncio
import logging
import time
import hashlib
import hmac
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import jwt
from functools import wraps

class RequestType(Enum):
    """Types of requests that can be processed"""
    JOB_SEARCH = "job_search"
    WEB_RESEARCH = "web_research"
    MATH_CALCULATION = "math_calculation"
    USER_PROFILE = "user_profile"
    SYSTEM_STATUS = "system_status"
    AGENT_COORDINATION = "agent_coordination"

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int
    requests_per_hour: int
    burst_limit: int
    window_size: int = 60  # seconds

@dataclass
class UserSession:
    """User session information"""
    user_id: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    request_count: int = 0
    is_authenticated: bool = False
    permissions: List[str] = None

class APIGateway:
    """
    Centralized API Gateway for FreelanceX.AI
    Handles routing, rate limiting, authentication, and security
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger("FreelanceX.APIGateway")
        
        # Rate limiting storage
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, UserSession] = {}
        
        # Request routing
        self.routes: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        
        # Security
        self.secret_key = self.config.get('secret_key', 'freelancex-secret-key')
        self.allowed_origins = self.config.get('allowed_origins', ['*'])
        
        # Performance monitoring
        self.request_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'average_response_time': 0.0
        }
        
        self._setup_routes()
        self._setup_middleware()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the API Gateway"""
        return {
            'secret_key': 'freelancex-secret-key-change-in-production',
            'allowed_origins': ['*'],
            'rate_limits': {
                'default': RateLimitConfig(60, 1000, 10),
                'job_search': RateLimitConfig(30, 500, 5),
                'web_research': RateLimitConfig(20, 300, 3),
                'math_calculation': RateLimitConfig(100, 2000, 20)
            },
            'timeout': 30,
            'max_request_size': 1024 * 1024  # 1MB
        }
    
    def _setup_routes(self):
        """Setup default routing configuration"""
        self.routes = {
            RequestType.JOB_SEARCH.value: self._route_job_search,
            RequestType.WEB_RESEARCH.value: self._route_web_research,
            RequestType.MATH_CALCULATION.value: self._route_math_calculation,
            RequestType.USER_PROFILE.value: self._route_user_profile,
            RequestType.SYSTEM_STATUS.value: self._route_system_status,
            RequestType.AGENT_COORDINATION.value: self._route_agent_coordination
        }
    
    def _setup_middleware(self):
        """Setup middleware chain"""
        self.middleware = [
            self._authenticate_request,
            self._rate_limit_check,
            self._validate_request,
            self._log_request
        ]
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main request processing pipeline
        """
        start_time = time.time()
        self.request_metrics['total_requests'] += 1
        
        try:
            # Extract request details
            request_type = request.get('type')
            user_id = request.get('user_id', 'anonymous')
            session_id = request.get('session_id')
            
            # Apply middleware
            for middleware_func in self.middleware:
                result = await middleware_func(request)
                if result.get('status') == 'error':
                    return result
            
            # Route request
            if request_type in self.routes:
                response = await self.routes[request_type](request)
            else:
                response = {
                    'status': 'error',
                    'message': f'Unknown request type: {request_type}',
                    'code': 400
                }
            
            # Update metrics
            response_time = time.time() - start_time
            self._update_response_time_metrics(response_time)
            
            if response.get('status') == 'success':
                self.request_metrics['successful_requests'] += 1
            else:
                self.request_metrics['failed_requests'] += 1
            
            return response
            
        except Exception as e:
            self.logger.error(f"Request processing error: {str(e)}")
            self.request_metrics['failed_requests'] += 1
            return {
                'status': 'error',
                'message': 'Internal server error',
                'code': 500
            }
    
    async def _authenticate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate and validate user session"""
        user_id = request.get('user_id')
        session_id = request.get('session_id')
        token = request.get('token')
        
        # For now, allow anonymous requests with basic validation
        if user_id and session_id:
            if session_id not in self.user_sessions:
                # Create new session
                self.user_sessions[session_id] = UserSession(
                    user_id=user_id,
                    session_id=session_id,
                    created_at=datetime.now(),
                    last_activity=datetime.now(),
                    is_authenticated=True
                )
            else:
                # Update existing session
                session = self.user_sessions[session_id]
                session.last_activity = datetime.now()
                session.request_count += 1
        
        return {'status': 'success'}
    
    async def _rate_limit_check(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Check rate limits for the request"""
        request_type = request.get('type', 'default')
        user_id = request.get('user_id', 'anonymous')
        
        rate_config = self.config['rate_limits'].get(request_type, self.config['rate_limits']['default'])
        
        # Check rate limits
        if not self._is_rate_limit_allowed(user_id, request_type, rate_config):
            self.request_metrics['rate_limited_requests'] += 1
            return {
                'status': 'error',
                'message': 'Rate limit exceeded',
                'code': 429
            }
        
        return {'status': 'success'}
    
    async def _validate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate request structure and content"""
        required_fields = ['type']
        
        for field in required_fields:
            if field not in request:
                return {
                    'status': 'error',
                    'message': f'Missing required field: {field}',
                    'code': 400
                }
        
        # Check request size
        request_size = len(json.dumps(request))
        if request_size > self.config['max_request_size']:
            return {
                'status': 'error',
                'message': 'Request too large',
                'code': 413
            }
        
        return {'status': 'success'}
    
    async def _log_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Log request for audit purposes"""
        self.logger.info(f"Processing request: {request.get('type')} from {request.get('user_id', 'anonymous')}")
        return {'status': 'success'}
    
    def _is_rate_limit_allowed(self, user_id: str, request_type: str, config: RateLimitConfig) -> bool:
        """Check if request is within rate limits"""
        key = f"{user_id}:{request_type}"
        now = time.time()
        
        if key not in self.rate_limits:
            self.rate_limits[key] = {
                'requests': [],
                'last_reset': now
            }
        
        rate_data = self.rate_limits[key]
        
        # Clean old requests
        rate_data['requests'] = [req_time for req_time in rate_data['requests'] 
                               if now - req_time < config.window_size]
        
        # Check limits
        if len(rate_data['requests']) >= config.requests_per_minute:
            return False
        
        # Add current request
        rate_data['requests'].append(now)
        return True
    
    def _update_response_time_metrics(self, response_time: float):
        """Update average response time metrics"""
        current_avg = self.request_metrics['average_response_time']
        total_requests = self.request_metrics['total_requests']
        
        # Calculate new average
        new_avg = (current_avg * (total_requests - 1) + response_time) / total_requests
        self.request_metrics['average_response_time'] = new_avg
    
    # Route handlers
    async def _route_job_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route job search requests to JobSearchAgent"""
        return {
            'status': 'success',
            'route': 'job_search_agent',
            'data': request.get('data', {})
        }
    
    async def _route_web_research(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route web research requests to WebSearchAgent"""
        return {
            'status': 'success',
            'route': 'web_search_agent',
            'data': request.get('data', {})
        }
    
    async def _route_math_calculation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route math calculation requests to MathAgent"""
        return {
            'status': 'success',
            'route': 'math_agent',
            'data': request.get('data', {})
        }
    
    async def _route_user_profile(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route user profile requests to memory layer"""
        return {
            'status': 'success',
            'route': 'user_profile',
            'data': request.get('data', {})
        }
    
    async def _route_system_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route system status requests"""
        return {
            'status': 'success',
            'route': 'system_status',
            'data': self.get_system_metrics()
        }
    
    async def _route_agent_coordination(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route agent coordination requests"""
        return {
            'status': 'success',
            'route': 'agent_coordination',
            'data': request.get('data', {})
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return {
            'request_metrics': self.request_metrics,
            'active_sessions': len(self.user_sessions),
            'rate_limits': len(self.rate_limits),
            'uptime': datetime.now().isoformat()
        }
    
    def create_session_token(self, user_id: str, session_id: str) -> str:
        """Create JWT token for user session"""
        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None