"""Integration Manager - OpenAI Agent SDK Integration Patterns
Handles integrations with external systems, MCP servers, and advanced tool connections
"""

import asyncio
import logging
import json
import aiohttp
from typing import Dict, Any, List, Optional, Callable, Union
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from agents import Agent, function_tool as tool
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced Pydantic models for integration management
class IntegrationConfig(BaseModel):
    """Configuration for external integrations"""
    name: str = Field(..., description="Integration name")
    type: str = Field(..., description="Integration type (mcp, api, database, etc.)")
    endpoint: str = Field(..., description="Integration endpoint")
    credentials: Dict[str, str] = Field(default_factory=dict, description="Authentication credentials")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    enabled: bool = Field(default=True, description="Whether integration is enabled")
    description: str = Field(default="", description="Integration description")
    version: str = Field(default="1.0", description="Integration version")
    health_check_interval: int = Field(default=300, description="Health check interval in seconds")

class IntegrationStatus(BaseModel):
    """Status information for an integration"""
    name: str = Field(..., description="Integration name")
    status: str = Field(..., description="Current status (connected, disconnected, error)")
    last_check: datetime = Field(..., description="Last health check timestamp")
    response_time: float = Field(default=0.0, description="Last response time in seconds")
    error_count: int = Field(default=0, description="Number of consecutive errors")
    uptime: float = Field(default=0.0, description="Uptime percentage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional status metadata")

class IntegrationMetrics(BaseModel):
    """Performance metrics for integrations"""
    total_requests: int = Field(default=0, description="Total number of requests")
    successful_requests: int = Field(default=0, description="Number of successful requests")
    failed_requests: int = Field(default=0, description="Number of failed requests")
    average_response_time: float = Field(default=0.0, description="Average response time")
    last_request_time: Optional[datetime] = Field(default=None, description="Last request timestamp")
    success_rate: float = Field(default=1.0, description="Success rate percentage")

class MCPToolInfo(BaseModel):
    """Information about MCP tools"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    return_type: str = Field(default="any", description="Return type")
    category: str = Field(default="general", description="Tool category")

# Enhanced MCP Server integration
class MCPServerIntegration:
    """Integration with MCP (Model Context Protocol) servers"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.connection = None
        self.available_tools: List[MCPToolInfo] = []
        self.status = IntegrationStatus(
            name=config.name,
            status="disconnected",
            last_check=datetime.now()
        )
        self.metrics = IntegrationMetrics()
        
    async def connect(self) -> bool:
        """Connect to MCP server with enhanced error handling"""
        try:
            logger.info(f"Connecting to MCP server: {self.config.endpoint}")
            start_time = datetime.now()
            
            # Simulate MCP connection with timeout
            await asyncio.wait_for(asyncio.sleep(0.1), timeout=self.config.timeout)
            
            self.connection = {
                "status": "connected", 
                "timestamp": datetime.now(),
                "endpoint": self.config.endpoint
            }
            
            # Discover available tools
            self.available_tools = await self._discover_tools()
            
            # Update status
            response_time = (datetime.now() - start_time).total_seconds()
            self.status.status = "connected"
            self.status.last_check = datetime.now()
            self.status.response_time = response_time
            self.status.error_count = 0
            
            self.metrics.successful_requests += 1
            self.metrics.last_request_time = datetime.now()
            
            logger.info(f"Successfully connected to MCP server: {self.config.name}")
            logger.info(f"Discovered {len(self.available_tools)} MCP tools")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"MCP connection timed out: {self.config.name}")
            self._update_error_status("Connection timeout")
            return False
        except Exception as e:
            logger.error(f"MCP connection failed for {self.config.name}: {str(e)}")
            self._update_error_status(str(e))
            return False
    
    def _update_error_status(self, error_message: str):
        """Update status with error information"""
        self.status.status = "error"
        self.status.last_check = datetime.now()
        self.status.error_count += 1
        self.status.metadata["last_error"] = error_message
        self.metrics.failed_requests += 1
    
    async def _discover_tools(self) -> List[MCPToolInfo]:
        """Discover available tools from MCP server with enhanced discovery"""
        try:
            # Simulate tool discovery with detailed information
            tools_data = [
                {
                    "name": "mcp_file_read",
                    "description": "Read file contents from the filesystem",
                    "parameters": {"path": "string", "encoding": "string"},
                    "return_type": "string",
                    "category": "filesystem"
                },
                {
                    "name": "mcp_file_write",
                    "description": "Write content to a file",
                    "parameters": {"path": "string", "content": "string", "mode": "string"},
                    "return_type": "boolean",
                    "category": "filesystem"
                },
                {
                    "name": "mcp_directory_list",
                    "description": "List contents of a directory",
                    "parameters": {"path": "string", "recursive": "boolean"},
                    "return_type": "array",
                    "category": "filesystem"
                },
                {
                    "name": "mcp_process_run",
                    "description": "Run a system process",
                    "parameters": {"command": "string", "args": "array", "cwd": "string"},
                    "return_type": "object",
                    "category": "system"
                },
                {
                    "name": "mcp_network_request",
                    "description": "Make HTTP requests",
                    "parameters": {"url": "string", "method": "string", "headers": "object"},
                    "return_type": "object",
                    "category": "network"
                }
            ]
            
            return [MCPToolInfo(**tool_data) for tool_data in tools_data]
            
        except Exception as e:
            logger.error(f"Tool discovery failed: {str(e)}")
            return []
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool with enhanced error handling and metrics"""
        start_time = datetime.now()
        
        try:
            if not self.connection:
                raise Exception("Not connected to MCP server")
            
            # Validate tool exists
            tool_info = next((tool for tool in self.available_tools if tool.name == tool_name), None)
            if not tool_info:
                raise Exception(f"Tool not found: {tool_name}")
            
            logger.info(f"Executing MCP tool: {tool_name} with parameters: {parameters}")
            
            # Simulate tool execution with dynamic results
            await asyncio.sleep(0.1)
            
            # Generate dynamic results based on tool type
            result = self._generate_tool_result(tool_name, parameters)
            
            # Update metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self.metrics.successful_requests += 1
            self.metrics.last_request_time = datetime.now()
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.successful_requests - 1) + response_time) 
                / self.metrics.successful_requests
            )
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "execution_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "tool_info": tool_info.dict()
            }
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            self.metrics.failed_requests += 1
            logger.error(f"MCP tool execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_tool_result(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Generate dynamic tool results based on tool type and parameters"""
        if tool_name == "mcp_file_read":
            path = parameters.get("path", "unknown")
            return f"Content of file: {path}\nThis is simulated file content for demonstration purposes."
        
        elif tool_name == "mcp_file_write":
            path = parameters.get("path", "unknown")
            content = parameters.get("content", "")
            return f"Successfully wrote {len(content)} characters to {path}"
        
        elif tool_name == "mcp_directory_list":
            path = parameters.get("path", "/")
            recursive = parameters.get("recursive", False)
            files = ["file1.txt", "file2.py", "directory1/", "directory2/"]
            if recursive:
                files.extend(["directory1/file3.txt", "directory2/file4.py"])
            return {"path": path, "files": files, "total_count": len(files)}
        
        elif tool_name == "mcp_process_run":
            command = parameters.get("command", "echo")
            args = parameters.get("args", ["hello"])
            return {
                "command": command,
                "args": args,
                "exit_code": 0,
                "stdout": f"Simulated output from {command}",
                "stderr": ""
            }
        
        elif tool_name == "mcp_network_request":
            url = parameters.get("url", "https://example.com")
            method = parameters.get("method", "GET")
            return {
                "status_code": 200,
                "headers": {"content-type": "application/json"},
                "body": f"Simulated response from {url}",
                "method": method
            }
        
        else:
            return f"Simulated result for {tool_name}"
    
    async def health_check(self) -> bool:
        """Perform health check on MCP server"""
        try:
            start_time = datetime.now()
            
            # Simulate health check
            await asyncio.sleep(0.05)
            
            response_time = (datetime.now() - start_time).total_seconds()
            self.status.last_check = datetime.now()
            self.status.response_time = response_time
            
            if self.connection:
                self.status.status = "connected"
                self.status.error_count = 0
                return True
            else:
                self.status.status = "disconnected"
                return False
                
        except Exception as e:
            self._update_error_status(f"Health check failed: {str(e)}")
            return False
    
    def get_status(self) -> IntegrationStatus:
        """Get current integration status"""
        return self.status
    
    def get_metrics(self) -> IntegrationMetrics:
        """Get integration metrics"""
        return self.metrics

# Enhanced External API integration
class ExternalAPIIntegration:
    """Integration with external APIs with enhanced capabilities"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.session = None
        self.status = IntegrationStatus(
            name=config.name,
            status="disconnected",
            last_check=datetime.now()
        )
        self.metrics = IntegrationMetrics()
        self.rate_limit_info = {
            "requests_per_minute": 60,
            "requests_remaining": 60,
            "reset_time": datetime.now() + timedelta(minutes=1)
        }
        
    async def __aenter__(self):
        """Async context manager entry with session management"""
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self._get_default_headers()
            )
            self.status.status = "connected"
            return self
        except Exception as e:
            logger.error(f"Failed to create API session: {str(e)}")
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        if self.session:
            await self.session.close()
            self.status.status = "disconnected"
    
    async def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, 
                          headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make HTTP request to external API with enhanced features"""
        start_time = datetime.now()
        
        try:
            # Check rate limits
            if not self._check_rate_limit():
                raise Exception("Rate limit exceeded")
            
            url = f"{self.config.endpoint}{endpoint}"
            request_headers = self._get_headers()
            if headers:
                request_headers.update(headers)
            
            logger.info(f"Making {method} request to {url}")
            
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers
            ) as response:
                response_time = (datetime.now() - start_time).total_seconds()
                
                if response.status == 200:
                    result = await response.json()
                    self._update_success_metrics(response_time)
                    
                    return {
                        "success": True,
                        "status_code": response.status,
                        "data": result,
                        "response_time": response_time,
                        "headers": dict(response.headers)
                    }
                else:
                    error_text = await response.text()
                    self._update_error_metrics(response_time)
                    raise Exception(f"API request failed: {response.status} - {error_text}")
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_error_metrics(response_time)
            logger.error(f"External API request failed: {str(e)}")
            raise
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        now = datetime.now()
        
        # Reset rate limit if time has passed
        if now >= self.rate_limit_info["reset_time"]:
            self.rate_limit_info["requests_remaining"] = self.rate_limit_info["requests_per_minute"]
            self.rate_limit_info["reset_time"] = now + timedelta(minutes=1)
        
        if self.rate_limit_info["requests_remaining"] > 0:
            self.rate_limit_info["requests_remaining"] -= 1
            return True
        
        return False
    
    def _update_success_metrics(self, response_time: float):
        """Update metrics for successful request"""
        self.metrics.successful_requests += 1
        self.metrics.last_request_time = datetime.now()
        self.metrics.average_response_time = (
            (self.metrics.average_response_time * (self.metrics.successful_requests - 1) + response_time) 
            / self.metrics.successful_requests
        )
        self.metrics.success_rate = (
            self.metrics.successful_requests / 
            (self.metrics.successful_requests + self.metrics.failed_requests)
        )
    
    def _update_error_metrics(self, response_time: float):
        """Update metrics for failed request"""
        self.metrics.failed_requests += 1
        self.metrics.last_request_time = datetime.now()
        self.metrics.success_rate = (
            self.metrics.successful_requests / 
            (self.metrics.successful_requests + self.metrics.failed_requests)
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        return {
            "Content-Type": "application/json",
            "User-Agent": f"FreelanceX.AI-Integration/{self.config.version}",
            "Accept": "application/json"
        }

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = self._get_default_headers()
        
        if "api_key" in self.config.credentials:
            headers["Authorization"] = f"Bearer {self.config.credentials['api_key']}"
        elif "username" in self.config.credentials and "password" in self.config.credentials:
            import base64
            auth_string = f"{self.config.credentials['username']}:{self.config.credentials['password']}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            headers["Authorization"] = f"Basic {auth_b64}"
        elif "client_id" in self.config.credentials and "client_secret" in self.config.credentials:
            headers["X-Client-ID"] = self.config.credentials["client_id"]
            headers["X-Client-Secret"] = self.config.credentials["client_secret"]
            
        return headers

# Enhanced Database integration
class DatabaseIntegration:
    """Integration with external databases with enhanced capabilities"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.connection = None
        self.status = IntegrationStatus(
            name=config.name,
            status="disconnected",
            last_check=datetime.now()
        )
        self.metrics = IntegrationMetrics()
        self.connection_pool = []
        self.max_connections = 10
        
    async def connect(self) -> bool:
        """Connect to database with connection pooling"""
        try:
            logger.info(f"Connecting to database: {self.config.endpoint}")
            start_time = datetime.now()
            
            # Simulate database connection with connection pooling
            await asyncio.sleep(0.1)
            
            self.connection = {
                "status": "connected", 
                "timestamp": datetime.now(),
                "endpoint": self.config.endpoint,
                "connection_id": f"db_{len(self.connection_pool) + 1}"
            }
            
            self.connection_pool.append(self.connection)
            
            # Update status
            response_time = (datetime.now() - start_time).total_seconds()
            self.status.status = "connected"
            self.status.last_check = datetime.now()
            self.status.response_time = response_time
            self.status.error_count = 0
            
            self.metrics.successful_requests += 1
            self.metrics.last_request_time = datetime.now()
            
            logger.info(f"Successfully connected to database: {self.config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed for {self.config.name}: {str(e)}")
            self._update_error_status(str(e))
            return False
    
    def _update_error_status(self, error_message: str):
        """Update status with error information"""
        self.status.status = "error"
        self.status.last_check = datetime.now()
        self.status.error_count += 1
        self.status.metadata["last_error"] = error_message
        self.metrics.failed_requests += 1
    
    async def execute_query(self, query: str, parameters: Dict[str, Any] = None, 
                           query_type: str = "select") -> List[Dict[str, Any]]:
        """Execute database query with enhanced features"""
        start_time = datetime.now()
        
        try:
            if not self.connection:
                raise Exception("Not connected to database")
            
            logger.info(f"Executing {query_type} query: {query[:50]}...")
            
            # Simulate query execution with dynamic results
            await asyncio.sleep(0.1)
            
            # Generate dynamic results based on query type
            results = self._generate_query_results(query, query_type, parameters)
            
            # Update metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self.metrics.successful_requests += 1
            self.metrics.last_request_time = datetime.now()
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.successful_requests - 1) + response_time) 
                / self.metrics.successful_requests
            )
            
            return results
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            self.metrics.failed_requests += 1
            logger.error(f"Database query failed: {str(e)}")
            raise
    
    def _generate_query_results(self, query: str, query_type: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate dynamic query results based on query type"""
        if query_type.lower() == "select":
            # Simulate SELECT query results
            return [
                {
                    "id": 1,
                    "name": "Sample User",
                    "email": "user@example.com",
                    "created_at": datetime.now().isoformat(),
                    "status": "active"
                },
                {
                    "id": 2,
                    "name": "Another User",
                    "email": "another@example.com",
                    "created_at": datetime.now().isoformat(),
                    "status": "inactive"
                }
            ]
        elif query_type.lower() == "insert":
            # Simulate INSERT query result
            return [{"inserted_id": 123, "affected_rows": 1}]
        elif query_type.lower() == "update":
            # Simulate UPDATE query result
            return [{"affected_rows": 1, "updated_at": datetime.now().isoformat()}]
        elif query_type.lower() == "delete":
            # Simulate DELETE query result
            return [{"affected_rows": 1, "deleted_at": datetime.now().isoformat()}]
        else:
            return [{"result": "Query executed successfully", "query_type": query_type}]
    
    async def health_check(self) -> bool:
        """Perform health check on database"""
        try:
            start_time = datetime.now()
            
            # Simulate health check with simple query
            await self.execute_query("SELECT 1", {}, "select")
            
            response_time = (datetime.now() - start_time).total_seconds()
            self.status.last_check = datetime.now()
            self.status.response_time = response_time
            self.status.status = "connected"
            self.status.error_count = 0
            
            return True
                
        except Exception as e:
            self._update_error_status(f"Health check failed: {str(e)}")
            return False
    
    def get_status(self) -> IntegrationStatus:
        """Get current integration status"""
        return self.status
    
    def get_metrics(self) -> IntegrationMetrics:
        """Get integration metrics"""
        return self.metrics

# Enhanced Integration manager
class IntegrationManager:
    """Manages all external integrations with enhanced capabilities"""
    
    def __init__(self):
        self.integrations: Dict[str, Any] = {}
        self.mcp_servers: Dict[str, MCPServerIntegration] = {}
        self.api_integrations: Dict[str, ExternalAPIIntegration] = {}
        self.database_integrations: Dict[str, DatabaseIntegration] = {}
        self.health_check_task = None
        self.manager_metrics = {
            "total_integrations": 0,
            "active_integrations": 0,
            "failed_integrations": 0,
            "last_health_check": None
        }
        
    async def add_integration(self, config: IntegrationConfig) -> bool:
        """Add new integration with enhanced validation"""
        try:
            logger.info(f"Adding integration: {config.name} ({config.type})")
            
            if config.name in self.integrations:
                raise ValueError(f"Integration already exists: {config.name}")
            
            if config.type == "mcp":
                integration = MCPServerIntegration(config)
                success = await integration.connect()
                if success:
                    self.mcp_servers[config.name] = integration
                    self.integrations[config.name] = integration
                    self.manager_metrics["total_integrations"] += 1
                    self.manager_metrics["active_integrations"] += 1
                    logger.info(f"Successfully added MCP integration: {config.name}")
                    return True
                else:
                    self.manager_metrics["failed_integrations"] += 1
                    return False
                
            elif config.type == "api":
                integration = ExternalAPIIntegration(config)
                self.api_integrations[config.name] = integration
                self.integrations[config.name] = integration
                self.manager_metrics["total_integrations"] += 1
                self.manager_metrics["active_integrations"] += 1
                logger.info(f"Successfully added API integration: {config.name}")
                return True
                
            elif config.type == "database":
                integration = DatabaseIntegration(config)
                success = await integration.connect()
                if success:
                    self.database_integrations[config.name] = integration
                    self.integrations[config.name] = integration
                    self.manager_metrics["total_integrations"] += 1
                    self.manager_metrics["active_integrations"] += 1
                    logger.info(f"Successfully added database integration: {config.name}")
                    return True
                else:
                    self.manager_metrics["failed_integrations"] += 1
                    return False
                
            else:
                raise ValueError(f"Unsupported integration type: {config.type}")
            
        except Exception as e:
            logger.error(f"Failed to add integration {config.name}: {str(e)}")
            self.manager_metrics["failed_integrations"] += 1
            return False
    
    async def remove_integration(self, integration_name: str) -> bool:
        """Remove integration with cleanup"""
        try:
            if integration_name not in self.integrations:
                raise ValueError(f"Integration not found: {integration_name}")
            
            integration = self.integrations[integration_name]
            
            # Cleanup based on integration type
            if integration_name in self.mcp_servers:
                del self.mcp_servers[integration_name]
            elif integration_name in self.api_integrations:
                del self.api_integrations[integration_name]
            elif integration_name in self.database_integrations:
                del self.database_integrations[integration_name]
            
            del self.integrations[integration_name]
            self.manager_metrics["total_integrations"] -= 1
            self.manager_metrics["active_integrations"] -= 1
            
            logger.info(f"Successfully removed integration: {integration_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove integration {integration_name}: {str(e)}")
            return False
    
    async def execute_mcp_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool with enhanced error handling"""
        if server_name not in self.mcp_servers:
            raise ValueError(f"MCP server not found: {server_name}")
        
        server = self.mcp_servers[server_name]
        
        # Check server health before execution
        if server.status.status != "connected":
            await server.connect()
        
        return await server.execute_tool(tool_name, parameters)
    
    async def make_api_request(self, integration_name: str, method: str, endpoint: str, 
                              data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make API request with enhanced features"""
        if integration_name not in self.api_integrations:
            raise ValueError(f"API integration not found: {integration_name}")
        
        async with self.api_integrations[integration_name] as api:
            return await api.make_request(method, endpoint, data, headers)
    
    async def execute_database_query(self, integration_name: str, query: str, 
                                   parameters: Dict[str, Any] = None, query_type: str = "select") -> List[Dict[str, Any]]:
        """Execute database query with enhanced features"""
        if integration_name not in self.database_integrations:
            raise ValueError(f"Database integration not found: {integration_name}")
        
        db = self.database_integrations[integration_name]
        
        # Check database health before execution
        if db.status.status != "connected":
            await db.connect()
        
        return await db.execute_query(query, parameters, query_type)
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all integrations"""
        logger.info("Starting health check for all integrations")
        start_time = datetime.now()
        
        health_results = {
            "timestamp": start_time.isoformat(),
            "total_integrations": len(self.integrations),
            "healthy_integrations": 0,
            "unhealthy_integrations": 0,
            "results": {}
        }
        
        # Check MCP servers
        for name, server in self.mcp_servers.items():
            try:
                is_healthy = await server.health_check()
                health_results["results"][name] = {
                    "type": "mcp",
                    "healthy": is_healthy,
                    "status": server.get_status().dict(),
                    "metrics": server.get_metrics().dict()
                }
                if is_healthy:
                    health_results["healthy_integrations"] += 1
                else:
                    health_results["unhealthy_integrations"] += 1
            except Exception as e:
                health_results["results"][name] = {
                    "type": "mcp",
                    "healthy": False,
                    "error": str(e)
                }
                health_results["unhealthy_integrations"] += 1
        
        # Check API integrations
        for name, api in self.api_integrations.items():
            try:
                health_results["results"][name] = {
                    "type": "api",
                    "healthy": True,  # API integrations are healthy if they can create sessions
                    "status": api.status.dict(),
                    "metrics": api.metrics.dict()
                }
                health_results["healthy_integrations"] += 1
            except Exception as e:
                health_results["results"][name] = {
                    "type": "api",
                    "healthy": False,
                    "error": str(e)
                }
                health_results["unhealthy_integrations"] += 1
        
        # Check database integrations
        for name, db in self.database_integrations.items():
            try:
                is_healthy = await db.health_check()
                health_results["results"][name] = {
                    "type": "database",
                    "healthy": is_healthy,
                    "status": db.get_status().dict(),
                    "metrics": db.get_metrics().dict()
                }
                if is_healthy:
                    health_results["healthy_integrations"] += 1
                else:
                    health_results["unhealthy_integrations"] += 1
            except Exception as e:
                health_results["results"][name] = {
                    "type": "database",
                    "healthy": False,
                    "error": str(e)
                }
                health_results["unhealthy_integrations"] += 1
        
        health_results["duration"] = (datetime.now() - start_time).total_seconds()
        self.manager_metrics["last_health_check"] = datetime.now()
        
        logger.info(f"Health check completed: {health_results['healthy_integrations']} healthy, {health_results['unhealthy_integrations']} unhealthy")
        return health_results
    
    def get_available_integrations(self) -> Dict[str, List[str]]:
        """Get list of available integrations with status"""
        return {
            "mcp_servers": list(self.mcp_servers.keys()),
            "api_integrations": list(self.api_integrations.keys()),
            "database_integrations": list(self.database_integrations.keys()),
            "total_count": len(self.integrations)
        }
    
    def get_integration_status(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific integration"""
        if integration_name not in self.integrations:
            return None
        
        integration = self.integrations[integration_name]
        
        if hasattr(integration, 'get_status') and hasattr(integration, 'get_metrics'):
            return {
                "name": integration_name,
                "status": integration.get_status().dict(),
                "metrics": integration.get_metrics().dict()
            }
        
        return {"name": integration_name, "status": "unknown"}
    
    def get_manager_metrics(self) -> Dict[str, Any]:
        """Get integration manager metrics"""
        return {
            **self.manager_metrics,
            "integration_types": {
                "mcp_servers": len(self.mcp_servers),
                "api_integrations": len(self.api_integrations),
                "database_integrations": len(self.database_integrations)
            }
        }

# Enhanced Integration tools for agents
@tool
async def list_available_integrations() -> Dict[str, List[str]]:
    """List all available integrations with enhanced information"""
    # This would be called with the integration manager instance
    # For now, return sample data with more details
    return {
        "mcp_servers": ["filesystem_server", "process_server", "network_server"],
        "api_integrations": ["upwork_api", "linkedin_api", "github_api", "stripe_api"],
        "database_integrations": ["user_database", "analytics_database", "cache_database"],
        "total_count": 10,
        "health_status": "monitoring"
    }

@tool
async def execute_mcp_tool(server_name: str, tool_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute MCP tool on specified server with enhanced error handling"""
    # This would use the integration manager
    # For now, return sample response with more details
    return {
        "success": True,
        "server": server_name,
        "tool": tool_name,
        "parameters": parameters or {},
        "result": f"Simulated result from {server_name}.{tool_name}",
        "execution_time": 0.15,
        "timestamp": datetime.now().isoformat(),
        "tool_info": {
            "name": tool_name,
            "category": "filesystem",
            "description": f"Simulated {tool_name} tool"
        }
    }

@tool
async def make_external_api_call(integration_name: str, method: str, endpoint: str, 
                                data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Make API call to external service with enhanced features"""
    # This would use the integration manager
    # For now, return sample response with more details
    return {
        "success": True,
        "integration": integration_name,
        "method": method,
        "endpoint": endpoint,
        "request_data": data or {},
        "request_headers": headers or {},
        "response": {
            "status_code": 200,
            "data": f"Simulated response from {integration_name}",
            "headers": {"content-type": "application/json"}
        },
        "response_time": 0.25,
        "timestamp": datetime.now().isoformat()
    }

@tool
async def check_integration_health(integration_name: str) -> Dict[str, Any]:
    """Check health status of a specific integration"""
    # This would use the integration manager
    # For now, return sample health check response
    return {
        "integration_name": integration_name,
        "healthy": True,
        "status": "connected",
        "last_check": datetime.now().isoformat(),
        "response_time": 0.05,
        "error_count": 0,
        "uptime": 99.5,
        "metrics": {
            "total_requests": 150,
            "successful_requests": 148,
            "failed_requests": 2,
            "success_rate": 98.67,
            "average_response_time": 0.12
        }
    }

# Enhanced Integration agent
class IntegrationAgent(Agent):
    """Agent specialized for managing integrations with enhanced capabilities"""
    
    def __init__(self, integration_manager: IntegrationManager):
        tools = [
            list_available_integrations,
            execute_mcp_tool,
            make_external_api_call,
            check_integration_health
        ]
        
        super().__init__(
            name="Integration Manager",
            description="Manages external integrations and API connections with enhanced monitoring",
            instructions="""
            You are an advanced integration management agent for FreelanceX.AI.
            
            Your responsibilities include:
            1. Managing connections to external services, MCP servers, and APIs
            2. Monitoring integration health and performance
            3. Executing tools and API calls with proper error handling
            4. Providing detailed status and metrics for all integrations
            5. Ensuring optimal performance and reliability of external connections
            
            When working with integrations:
            - Always validate integration availability before use
            - Monitor response times and success rates
            - Handle errors gracefully with detailed error messages
            - Provide comprehensive status information
            - Optimize requests for performance and reliability
            
            You have access to MCP servers, external APIs, and database connections.
            Always check integration health before attempting operations and provide
            detailed feedback on the success or failure of integration operations.
            """,
            tools=tools
        )
        
        self.integration_manager = integration_manager

# Example integration configurations with enhanced details
def get_sample_integrations() -> List[IntegrationConfig]:
    """Get sample integration configurations with enhanced details"""
    return [
        IntegrationConfig(
            name="filesystem_mcp",
            type="mcp",
            endpoint="ws://localhost:3000",
            credentials={},
            description="File system MCP server for file operations",
            version="1.2.0",
            health_check_interval=60
        ),
        IntegrationConfig(
            name="upwork_api",
            type="api",
            endpoint="https://api.upwork.com",
            credentials={"api_key": "your_upwork_api_key"},
            description="Upwork API integration for job data",
            version="2.1.0",
            health_check_interval=300
        ),
        IntegrationConfig(
            name="user_database",
            type="database",
            endpoint="postgresql://localhost:5432/freelancex",
            credentials={"username": "user", "password": "pass"},
            description="User database for authentication and profiles",
            version="1.0.0",
            health_check_interval=120
        ),
        IntegrationConfig(
            name="stripe_api",
            type="api",
            endpoint="https://api.stripe.com",
            credentials={"api_key": "your_stripe_secret_key"},
            description="Stripe API for payment processing",
            version="2023-10-16",
            health_check_interval=180
        )
    ]
