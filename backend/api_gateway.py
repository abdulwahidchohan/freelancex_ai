#!/usr/bin/env python3
"""
FreelanceX.AI - API Gateway
Centralized request router, rate limiter, and security layer for the multi-agent system.
"""

import asyncio
import logging
import time
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import jwt
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import redis
from pydantic import BaseModel, ValidationError

# Import FreelanceX.AI components
from core.agent_manager import AgentManager
from core.base_agent import BaseAgent, AgentStatus

class RequestType(Enum):
    """Types of requests that can be routed"""
    JOB_SEARCH = "job_search"
    WEB_SEARCH = "web_search"
    MATH_CALCULATION = "math_calculation"
    USER_PROFILE = "user_profile"
    SYSTEM_STATUS = "system_status"
    AGENT_COORDINATION = "agent_coordination"
    MULTIMODAL = "multimodal"

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    window_size: int = 60  # seconds

@dataclass
class UserSession:
    """User session information"""
    user_id: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    request_count: int = 0
    rate_limit_reset: datetime = field(default_factory=datetime.now)
    permissions: List[str] = field(default_factory=list)

class RequestRouter:
    """Routes requests to appropriate agents based on content and type"""
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.logger = logging.getLogger("FreelanceX.API.Router")
        
        # Define routing rules
        self.routing_rules = {
            RequestType.JOB_SEARCH: ["job_search_agent"],
            RequestType.WEB_SEARCH: ["web_search_agent"],
            RequestType.MATH_CALCULATION: ["math_agent"],
            RequestType.USER_PROFILE: ["user_clone_agent"],
            RequestType.SYSTEM_STATUS: ["executive_agent"],
            RequestType.AGENT_COORDINATION: ["executive_agent"],
            RequestType.MULTIMODAL: ["web_search_agent", "job_search_agent"]
        }
    
    async def route_request(self, request_type: RequestType, content: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate agent(s)"""
        try:
            target_agents = self.routing_rules.get(request_type, [])
            
            if not target_agents:
                raise ValueError(f"No routing rule found for request type: {request_type}")
            
            # For multimodal requests, coordinate multiple agents
            if request_type == RequestType.MULTIMODAL:
                return await self._coordinate_multiple_agents(target_agents, content)
            
            # Single agent routing
            agent_name = target_agents[0]
            agent = self.agent_manager.get_agent(agent_name)
            
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")
            
            result = await agent.process_request(content)
            return {
                "success": True,
                "agent": agent_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error routing request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _coordinate_multiple_agents(self, agent_names: List[str], content: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple agents for complex requests"""
        results = {}
        
        for agent_name in agent_names:
            agent = self.agent_manager.get_agent(agent_name)
            if agent:
                try:
                    result = await agent.process_request(content)
                    results[agent_name] = result
                except Exception as e:
                    self.logger.error(f"Error with agent {agent_name}: {str(e)}")
                    results[agent_name] = {"error": str(e)}
        
        return {
            "success": True,
            "coordinated_results": results,
            "timestamp": datetime.now().isoformat()
        }

class RateLimiter:
    """Handles rate limiting for API requests"""
    
    def __init__(self, redis_client: redis.Redis, config: RateLimitConfig):
        self.redis = redis_client
        self.config = config
        self.logger = logging.getLogger("FreelanceX.API.RateLimiter")
    
    async def check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limits"""
        try:
            current_time = int(time.time())
            window_start = current_time - self.config.window_size
            
            # Get current request count
            key = f"rate_limit:{user_id}:{window_start}"
            current_count = await self.redis.get(key)
            
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)
            
            # Check if limit exceeded
            if current_count >= self.config.requests_per_minute:
                return False
            
            # Increment counter
            await self.redis.incr(key)
            await self.redis.expire(key, self.config.window_size)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Rate limiting error: {str(e)}")
            return True  # Allow request if rate limiting fails
    
    async def get_rate_limit_info(self, user_id: str) -> Dict[str, Any]:
        """Get current rate limit information for user"""
        try:
            current_time = int(time.time())
            window_start = current_time - self.config.window_size
            
            key = f"rate_limit:{user_id}:{window_start}"
            current_count = await self.redis.get(key)
            
            return {
                "current_requests": int(current_count) if current_count else 0,
                "limit": self.config.requests_per_minute,
                "window_size": self.config.window_size,
                "reset_time": window_start + self.config.window_size
            }
            
        except Exception as e:
            self.logger.error(f"Error getting rate limit info: {str(e)}")
            return {"error": str(e)}

class SecurityManager:
    """Handles authentication and security"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.logger = logging.getLogger("FreelanceX.API.Security")
    
    def generate_token(self, user_id: str, permissions: List[str]) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == hashed

# Pydantic models for API requests/responses
class APIRequest(BaseModel):
    """Base API request model"""
    request_type: RequestType
    content: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class APIResponse(BaseModel):
    """Base API response model"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str
    rate_limit_info: Optional[Dict[str, Any]] = None

class FreelanceXAPIGateway:
    """Main API Gateway class"""
    
    def __init__(self, 
                 agent_manager: AgentManager,
                 redis_url: str = "redis://localhost:6379",
                 secret_key: str = "your-secret-key-here"):
        
        self.agent_manager = agent_manager
        self.logger = logging.getLogger("FreelanceX.API.Gateway")
        
        # Initialize components
        self.router = RequestRouter(agent_manager)
        self.redis_client = redis.from_url(redis_url)
        self.rate_limiter = RateLimiter(self.redis_client, RateLimitConfig())
        self.security_manager = SecurityManager(secret_key)
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="FreelanceX.AI API Gateway",
            description="Centralized API Gateway for FreelanceX.AI multi-agent system",
            version="1.0.0"
        )
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        # Session management
        self.active_sessions: Dict[str, UserSession] = {}
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure appropriately for production
        )
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.post("/api/v1/process", response_model=APIResponse)
        async def process_request(request: APIRequest, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
            """Main request processing endpoint"""
            try:
                # Verify authentication
                token_payload = self.security_manager.verify_token(credentials.credentials)
                user_id = token_payload.get("user_id")
                
                # Check rate limiting
                if not await self.rate_limiter.check_rate_limit(user_id):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                
                # Route request
                result = await self.router.route_request(request.request_type, request.content)
                
                # Get rate limit info
                rate_limit_info = await self.rate_limiter.get_rate_limit_info(user_id)
                
                return APIResponse(
                    success=result.get("success", False),
                    data=result.get("result") if result.get("success") else None,
                    error=result.get("error"),
                    timestamp=datetime.now().isoformat(),
                    rate_limit_info=rate_limit_info
                )
                
            except Exception as e:
                self.logger.error(f"Error processing request: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "agents": len(self.agent_manager.get_all_agents()),
                "active_sessions": len(self.active_sessions)
            }
        
        @self.app.post("/api/v1/auth/login")
        async def login(username: str, password: str):
            """User login endpoint"""
            # This would typically validate against a database
            # For now, we'll use a simple example
            if username == "demo" and password == "password":
                token = self.security_manager.generate_token(username, ["read", "write"])
                return {"token": token, "user_id": username}
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
    
    async def start(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the API Gateway"""
        import uvicorn
        
        self.logger.info(f"Starting FreelanceX.AI API Gateway on {host}:{port}")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def shutdown(self):
        """Shutdown the API Gateway"""
        self.logger.info("Shutting down FreelanceX.AI API Gateway")
        # Close Redis connection
        self.redis_client.close()

# Middleware for request logging
async def log_request_middleware(request: Request, call_next: Callable):
    """Middleware to log all requests"""
    start_time = time.time()
    
    # Log request
    logging.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logging.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize agent manager (you'll need to implement this)
        agent_manager = AgentManager()
        
        # Create and start API Gateway
        gateway = FreelanceXAPIGateway(agent_manager)
        await gateway.start()
    
    asyncio.run(main())