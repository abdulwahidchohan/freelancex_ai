#!/usr/bin/env python3
"""
FreelanceX.AI API Gateway
Centralized API layer managing requests between frontend, backend agents, and external systems
Features: Request routing, rate limiting, authentication, security, monitoring
"""

import asyncio
import logging
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Depends, Request, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

import jwt
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Import FreelanceX.AI components
from core.agent_manager import AgentManager
from core.base_agent import BaseAgent, AgentStatus
from backend.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address)

@dataclass
class APIConfig:
    """API Gateway configuration"""
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    enable_cors: bool = True
    enable_https_redirect: bool = True
    trusted_hosts: List[str] = None

class UserAuthRequest(BaseModel):
    """User authentication request model"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class AgentRequest(BaseModel):
    """Agent request model"""
    agent_name: str
    action: str
    parameters: Dict[str, Any] = {}
    user_context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Agent response model"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    agent_name: str
    timestamp: str
    execution_time: float

class APIGateway:
    """
    Centralized API Gateway for FreelanceX.AI
    Manages routing, authentication, rate limiting, and security
    """
    
    def __init__(self, config: APIConfig = None):
        self.config = config or APIConfig()
        self.app = FastAPI(
            title="FreelanceX.AI API Gateway",
            description="Centralized API for FreelanceX.AI multi-agent system",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Initialize components
        self.agent_manager = AgentManager()
        self.db_manager = DatabaseManager()
        self.security = HTTPBearer()
        
        # Rate limiting and monitoring
        self.request_counts = defaultdict(int)
        self.blocked_ips = set()
        self.system_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "active_users": 0,
            "start_time": datetime.now()
        }
        
        self._setup_middleware()
        self._setup_routes()
        self._setup_error_handlers()
        
        logger.info("FreelanceX.AI API Gateway initialized")

    def _setup_middleware(self):
        """Configure middleware for security and performance"""
        # CORS middleware
        if self.config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],  # Configure based on environment
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Trusted hosts middleware
        if self.config.trusted_hosts:
            self.app.add_middleware(
                TrustedHostMiddleware, 
                allowed_hosts=self.config.trusted_hosts
            )
        
        # Rate limiting middleware
        self.app.state.limiter = limiter
        self.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        self.app.add_middleware(SlowAPIMiddleware)

    def _setup_error_handlers(self):
        """Setup custom error handlers"""
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            logger.warning(f"Validation error: {exc.errors()}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": "Request validation failed", "errors": exc.errors()}
            )
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            logger.error(f"HTTP error: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )

    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            """API Gateway health check"""
            return {
                "message": "FreelanceX.AI API Gateway",
                "status": "active",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/health")
        async def health_check():
            """Comprehensive health check"""
            return {
                "status": "healthy",
                "metrics": self.system_metrics,
                "agents": {name: agent.status.value for name, agent in self.agent_manager.agents.items()},
                "database": "connected" if self.db_manager.is_connected() else "disconnected"
            }
        
        @self.app.post("/auth/login", response_model=TokenResponse)
        @limiter.limit("5/minute")
        async def login(request: Request, auth_request: UserAuthRequest):
            """User authentication endpoint"""
            try:
                # Validate user credentials (implement proper authentication)
                if await self._validate_user(auth_request.username, auth_request.password):
                    tokens = await self._generate_tokens(auth_request.username)
                    
                    # Update metrics
                    self.system_metrics["active_users"] += 1
                    
                    return TokenResponse(**tokens)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials"
                    )
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication service error"
                )
        
        @self.app.post("/agents/{agent_name}/execute", response_model=AgentResponse)
        @limiter.limit("30/minute")
        async def execute_agent_action(
            request: Request,
            agent_name: str,
            agent_request: AgentRequest,
            current_user: dict = Depends(self._get_current_user)
        ):
            """Execute action on specific agent"""
            start_time = time.time()
            
            try:
                # Validate agent exists
                if agent_name not in self.agent_manager.agents:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Agent {agent_name} not found"
                    )
                
                # Route request to agent
                agent = self.agent_manager.agents[agent_name]
                result = await self._execute_agent_request(agent, agent_request, current_user)
                
                execution_time = time.time() - start_time
                
                # Update metrics
                self.system_metrics["successful_requests"] += 1
                self._update_average_response_time(execution_time)
                
                return AgentResponse(
                    success=True,
                    data=result,
                    agent_name=agent_name,
                    timestamp=datetime.now().isoformat(),
                    execution_time=execution_time
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Agent execution error: {str(e)}")
                
                # Update metrics
                self.system_metrics["failed_requests"] += 1
                
                return AgentResponse(
                    success=False,
                    error=str(e),
                    agent_name=agent_name,
                    timestamp=datetime.now().isoformat(),
                    execution_time=execution_time
                )
        
        @self.app.get("/agents")
        async def list_agents(current_user: dict = Depends(self._get_current_user)):
            """List all available agents and their status"""
            agents_info = {}
            for name, agent in self.agent_manager.agents.items():
                agents_info[name] = {
                    "status": agent.status.value,
                    "type": agent.agent_type,
                    "capabilities": getattr(agent, 'capabilities', []),
                    "last_activity": getattr(agent, 'last_activity', None)
                }
            return {"agents": agents_info}
        
        @self.app.post("/agents/negotiate")
        @limiter.limit("10/minute")
        async def initiate_agent_negotiation(
            request: Request,
            agent_a: str,
            agent_b: str,
            context: Dict[str, Any],
            current_user: dict = Depends(self._get_current_user)
        ):
            """Initiate negotiation between two agents"""
            try:
                negotiation_id = await self.agent_manager.initiate_negotiation(
                    agent_a, agent_b, context
                )
                
                if negotiation_id:
                    return {
                        "negotiation_id": negotiation_id,
                        "status": "initiated",
                        "participants": [agent_a, agent_b]
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to initiate negotiation"
                    )
                    
            except Exception as e:
                logger.error(f"Negotiation initiation error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Negotiation service error"
                )
        
        @self.app.get("/metrics")
        async def get_system_metrics(current_user: dict = Depends(self._get_current_user)):
            """Get system performance metrics"""
            uptime = datetime.now() - self.system_metrics["start_time"]
            
            return {
                **self.system_metrics,
                "uptime_seconds": uptime.total_seconds(),
                "requests_per_minute": self.system_metrics["total_requests"] / max(uptime.total_seconds() / 60, 1),
                "success_rate": (
                    self.system_metrics["successful_requests"] / 
                    max(self.system_metrics["total_requests"], 1) * 100
                )
            }

    async def _validate_user(self, username: str, password: str) -> bool:
        """Validate user credentials"""
        # Implement proper user validation with database
        # This is a placeholder implementation
        try:
            user_data = await self.db_manager.get_user_by_username(username)
            if user_data:
                # Hash password and compare
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                return password_hash == user_data.get('password_hash')
            return False
        except Exception as e:
            logger.error(f"User validation error: {str(e)}")
            return False

    async def _generate_tokens(self, username: str) -> Dict[str, Any]:
        """Generate access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token
        access_payload = {
            "sub": username,
            "exp": now + timedelta(minutes=self.config.access_token_expire_minutes),
            "iat": now,
            "type": "access"
        }
        access_token = jwt.encode(access_payload, self.config.secret_key, algorithm=self.config.algorithm)
        
        # Refresh token
        refresh_payload = {
            "sub": username,
            "exp": now + timedelta(days=self.config.refresh_token_expire_days),
            "iat": now,
            "type": "refresh"
        }
        refresh_token = jwt.encode(refresh_payload, self.config.secret_key, algorithm=self.config.algorithm)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": self.config.access_token_expire_minutes * 60
        }

    async def _get_current_user(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        """Get current user from token"""
        try:
            payload = jwt.decode(
                credentials.credentials, 
                self.config.secret_key, 
                algorithms=[self.config.algorithm]
            )
            username = payload.get("sub")
            if username is None or payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Get user data from database
            user_data = await self.db_manager.get_user_by_username(username)
            if user_data is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            return user_data
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    async def _execute_agent_request(self, agent: BaseAgent, request: AgentRequest, user_context: dict) -> Any:
        """Execute request on specific agent"""
        try:
            # Add user context to request parameters
            enhanced_params = {
                **request.parameters,
                "user_context": user_context,
                "request_id": secrets.token_urlsafe(16)
            }
            
            # Execute agent action based on request type
            if request.action == "process_message":
                result = await agent.process_message(enhanced_params.get("message", ""))
            elif request.action == "get_status":
                result = {"status": agent.status.value, "type": agent.agent_type}
            elif hasattr(agent, request.action):
                method = getattr(agent, request.action)
                if callable(method):
                    result = await method(**enhanced_params) if asyncio.iscoroutinefunction(method) else method(**enhanced_params)
                else:
                    raise ValueError(f"Invalid action: {request.action}")
            else:
                raise ValueError(f"Action {request.action} not supported by agent {agent.agent_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Agent execution error: {str(e)}")
            raise

    def _update_average_response_time(self, response_time: float):
        """Update average response time metric"""
        total_requests = self.system_metrics["total_requests"]
        current_avg = self.system_metrics["average_response_time"]
        
        new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        self.system_metrics["average_response_time"] = new_avg

    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the API Gateway server"""
        import uvicorn
        
        logger.info(f"Starting FreelanceX.AI API Gateway on {host}:{port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()

# Global API Gateway instance
api_gateway = APIGateway()

# Export for external use
app = api_gateway.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)